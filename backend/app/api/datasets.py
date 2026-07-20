from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from backend.app.api import deps
from backend.app.core.database import get_db
from backend.app.models.dataset import Dataset
from backend.app.models.project import Project
from backend.app.models.user import User
from backend.app.schemas.dataset import DatasetResponse
from backend.app.services.file_service import save_uploaded_file, profile_dataset
from backend.app.agents.cleaner import CleanerAgent
from backend.app.services.execution_service import execute_code_safely
import pandas as pd
import os

router = APIRouter()


@router.post("/upload", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
def upload_dataset(
    project_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Upload a data file to a project and trigger automatic type profiling."""
    # Ensure project exists and belongs to current user
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        # Save file to uploads folder
        file_path = save_uploaded_file(file, project_id)
        file_size = os.path.getsize(file_path)

        # Run profiling
        schema_json, profile_json, rows, cols = profile_dataset(file_path)

        dataset = Dataset(
            project_id=project_id,
            filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            row_count=rows,
            col_count=cols,
            schema_json=schema_json,
            profile_json=profile_json,
            version=1
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        return dataset

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process and profile dataset: {str(e)}"
        )


@router.get("/", response_model=List[DatasetResponse])
def list_datasets(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """List all uploaded datasets in a project."""
    # Ensure project belongs to user
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return db.query(Dataset).filter(Dataset.project_id == project_id).all()


@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Retrieve details, schema metadata, and quality profile of a dataset."""
    dataset = db.query(Dataset).join(Project).filter(
        Dataset.id == dataset_id,
        Project.user_id == current_user.id
    ).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@router.post("/{dataset_id}/clean", response_model=DatasetResponse)
def auto_clean_dataset(
    dataset_id: str,
    instruction: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Invoke the Data Cleaning Agent to propose and execute code to resolve data quality issues.
    Saves the output as a new dataset version.
    """
    dataset = db.query(Dataset).join(Project).filter(
        Dataset.id == dataset_id,
        Project.user_id == current_user.id
    ).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    try:
        # Load source file
        ext = os.path.splitext(dataset.file_path)[1].lower()
        if ext == ".csv":
            df = pd.read_csv(dataset.file_path)
        else:
            df = pd.read_excel(dataset.file_path)

        # Execute Cleaner Agent
        cleaner = CleanerAgent()
        cleaning_result = cleaner.clean_dataset(dataset.profile_json, instruction)

        code = cleaning_result.get("cleaning_code", "")
        if not code:
            raise ValueError("No cleaning code was returned by the Cleaner Agent.")

        # Run generated pandas code block
        exec_res = execute_code_safely(code, df)
        if not exec_res["success"]:
            raise RuntimeError(f"Cleaning execution failed: {exec_res['error']}")

        # Save result as a new file version
        new_filename = f"cleaned_v{dataset.version + 1}_{dataset.filename}"
        project_dir = os.path.dirname(dataset.file_path)
        new_filepath = os.path.join(project_dir, f"cleaned_v{dataset.version + 1}_{os.path.basename(dataset.file_path)}")

        # Retrieve dataframe from executor response
        # In execute_code_safely, table output format is:
        # { "columns": [...], "rows": [...], "total_rows": N }
        # Let's save the cleaned dataframe
        # Wait, since execute_code_safely runs on a copy of df, we should load df from variables or output.
        # Let's write the dataframe output back to file.
        # To make it robust, we can run the code block locally or get it from the result.
        # Actually, let's write a simple execution runner here or retrieve the modified df from the sandbox:
        sandbox = {"df": df, "pd": pd, "np": np}
        exec(code, sandbox)
        cleaned_df = sandbox["df"]

        if ext == ".csv":
            cleaned_df.to_csv(new_filepath, index=False)
        else:
            cleaned_df.to_excel(new_filepath, index=False)

        # Profile the cleaned dataset
        schema_json, profile_json, rows, cols = profile_dataset(new_filepath)

        new_dataset = Dataset(
            project_id=dataset.project_id,
            filename=new_filename,
            file_path=new_filepath,
            file_size=os.path.getsize(new_filepath),
            row_count=rows,
            col_count=cols,
            schema_json=schema_json,
            profile_json=profile_json,
            version=dataset.version + 1
        )
        db.add(new_dataset)
        db.commit()
        db.refresh(new_dataset)
        return new_dataset

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Auto-cleaning failed: {str(e)}"
        )
