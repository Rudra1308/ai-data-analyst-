import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.api import deps
from backend.app.core.database import get_db
from backend.app.models.chat import Conversation, Message
from backend.app.models.dataset import Dataset
from backend.app.models.project import Project
from backend.app.models.user import User
from backend.app.schemas.chat import (
    ConversationCreate,
    ConversationResponse,
    MessageRequest,
    MessageResponse
)
from backend.app.services.execution_service import execute_code_safely
from backend.app.agents import (
    PlannerAgent,
    EDAAgent,
    StatsAgent,
    MLAgent,
    ForecasterAgent,
    VisualizerAgent,
    InsightAgent
)
import pandas as pd

router = APIRouter()


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    conv_in: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Create a new chat conversation thread in a project."""
    project = db.query(Project).filter(Project.id == conv_in.project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    conversation = Conversation(
        project_id=conv_in.project_id,
        user_id=current_user.id,
        title=conv_in.title or "New Analysis"
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


@router.get("/conversations", response_model=List[ConversationResponse])
def list_conversations(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """List all chat conversations in a project."""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return db.query(Conversation).filter(Conversation.project_id == project_id).all()


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get conversation thread details and message history."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
def send_message(
    conversation_id: str,
    msg_in: MessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Submit a query about a dataset. Dispatches to the Planner Agent,
    orchestrates specialized agents to execute Python pandas code in the sandbox,
    runs the Insight Agent to construct business answers, and stores history.
    """
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if not msg_in.dataset_id:
        raise HTTPException(status_code=400, detail="dataset_id is required to perform analysis.")

    dataset = db.query(Dataset).filter(
        Dataset.id == msg_in.dataset_id,
        Dataset.project_id == conversation.project_id
    ).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found in this project.")

    # 1. Save user query message
    user_msg = Message(
        conversation_id=conversation_id,
        role="user",
        content=msg_in.content
    )
    db.add(user_msg)
    db.commit()

    try:
        # Load dataset into pandas
        if dataset.file_path.endswith(".csv"):
            df = pd.read_csv(dataset.file_path)
        else:
            df = pd.read_excel(dataset.file_path)

        # Resolve LLM configurations from user request
        provider = None
        model = None
        api_key = None
        
        if msg_in.model_settings:
            provider = msg_in.model_settings.get("provider")
            model = msg_in.model_settings.get("model")
            
        if msg_in.api_keys and provider:
            api_key = msg_in.api_keys.get(provider)

        # 2. Invoke Planner Agent to determine task sequence
        planner = PlannerAgent(provider=provider, model=model, api_key=api_key)
        plan = planner.plan_workflow(msg_in.content, dataset.profile_json)
        
        task_sequence = plan.get("task_sequence", [])
        reasoning_chain = plan.get("reasoning_chain", [])

        # Standard logs/execution trace
        execution_trace = {
            "intent": plan.get("intent"),
            "reasoning_chain": reasoning_chain,
            "agent_steps": []
        }

        last_code = ""
        last_result = None
        combined_execution_summary = ""

        # 3. Iterate tasks and run worker agents
        for step in task_sequence:
            agent_name = step.get("agent")
            task_desc = step.get("task")

            agent_response = {}
            code_to_run = ""

            if agent_name == "cleaner":
                cleaner = CleanerAgent(provider=provider, model=model, api_key=api_key)
                agent_response = cleaner.clean_dataset(dataset.profile_json, task_desc)
                code_to_run = agent_response.get("cleaning_code", "")

            elif agent_name == "eda":
                eda = EDAAgent(provider=provider, model=model, api_key=api_key)
                agent_response = eda.perform_eda(dataset.profile_json, task_desc)
                code_to_run = agent_response.get("code", "")

            elif agent_name == "stats":
                stats = StatsAgent(provider=provider, model=model, api_key=api_key)
                agent_response = stats.perform_stats_test(dataset.profile_json, task_desc)
                code_to_run = agent_response.get("code", "")

            elif agent_name == "ml":
                ml = MLAgent(provider=provider, model=model, api_key=api_key)
                agent_response = ml.run_ml_task(dataset.profile_json, task_desc)
                code_to_run = agent_response.get("code", "")

            elif agent_name == "forecaster":
                forecaster = ForecasterAgent(provider=provider, model=model, api_key=api_key)
                agent_response = forecaster.run_forecast(dataset.profile_json, task_desc)
                code_to_run = agent_response.get("code", "")

            elif agent_name == "visualizer":
                visualizer = VisualizerAgent(provider=provider, model=model, api_key=api_key)
                agent_response = visualizer.generate_chart(dataset.profile_json, task_desc)
                code_to_run = agent_response.get("code", "")

            # Execute code if produced
            if code_to_run:
                last_code = code_to_run
                run_res = execute_code_safely(code_to_run, df)
                last_result = run_res

                step_trace = {
                    "agent": agent_name,
                    "task": task_desc,
                    "code": code_to_run,
                    "success": run_res["success"],
                    "result_type": run_res["result_type"]
                }
                if not run_res["success"]:
                    step_trace["error"] = run_res["error"]
                    combined_execution_summary += f"\nAgent '{agent_name}' failed to run task with error: {run_res['error']}\n"
                else:
                    # Summarize intermediate results for InsightAgent context
                    if run_res["result_type"] == "dataframe":
                        data_summary = f"Returned Table with {run_res['data']['total_rows']} rows. Preview: {run_res['data']['rows'][:3]}"
                    elif run_res["result_type"] == "plotly":
                        data_summary = "Returned interactive Plotly chart figure successfully."
                    else:
                        data_summary = f"Value result: {run_res['data']}"
                    
                    combined_execution_summary += f"\nAgent '{agent_name}' successfully executed task: {task_desc}.\nResult context: {data_summary}\n"

                execution_trace["agent_steps"].append(step_trace)

        # 4. Generate report with Insight Agent
        insighter = InsightAgent(provider=provider, model=model, api_key=api_key)
        report = insighter.generate_report(msg_in.content, dataset.profile_json, combined_execution_summary)

        # Convert report to structured markdown description for storage
        report_markdown = f"""### Executive Summary
{report.get('executive_summary')}

### Business Insights
"""
        for insight in report.get("business_insights", []):
            report_markdown += f"- {insight}\n"

        if report.get("statistical_findings"):
            report_markdown += "\n### Statistical Findings\n"
            for finding in report.get("statistical_findings", []):
                report_markdown += f"- {finding}\n"

        report_markdown += f"\n**Confidence Level:** {report.get('confidence_level', 'medium').upper()}\n"

        if report.get("recommended_actions"):
            report_markdown += "\n### Recommended Actions\n"
            for action in report.get("recommended_actions", []):
                report_markdown += f"- {action}\n"

        if report.get("potential_risks"):
            report_markdown += "\n### Potential Risks\n"
            for risk in report.get("potential_risks", []):
                report_markdown += f"- {risk}\n"

        # Structured result container
        formatted_exec_result = {
            "success": True,
            "report_details": report,
            "visualization": last_result["data"] if last_result and last_result["result_type"] == "plotly" else None,
            "dataframe": last_result["data"] if last_result and last_result["result_type"] == "dataframe" else None,
            "scalar": last_result["data"] if last_result and last_result["result_type"] == "scalar" else None
        }

        # Save assistant message
        assistant_msg = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=report_markdown,
            generated_code=last_code,
            execution_result=formatted_exec_result,
            agent_metadata=execution_trace
        )
        db.add(assistant_msg)
        db.commit()
        db.refresh(assistant_msg)
        return assistant_msg

    except Exception as e:
        # Fallback error response
        error_msg = f"An error occurred while compiling analysis: {str(e)}"
        assistant_msg = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=error_msg,
            execution_result={"success": False, "error": str(e)}
        )
        db.add(assistant_msg)
        db.commit()
        db.refresh(assistant_msg)
        return assistant_msg
