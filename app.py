"""
AI Data Analyst — Main Streamlit Application
Upload your data. Ask questions. Get insights instantly.
"""
import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

from src.data_loader import load_csv, get_data_summary, get_sample_rows
from src.llm_engine import LLMEngine
from src.execution_engine import execute_code
from src.visualization import quick_eda
from src.utils import format_dataframe_info, OPENROUTER_MODELS

# ── Load environment variables ──────────────────────────────────────────
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

# ── Page Configuration ──────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load Custom CSS ─────────────────────────────────────────────────────
css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Session State Initialization ────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "df" not in st.session_state:
    st.session_state.df = None
if "llm" not in st.session_state:
    st.session_state.llm = None
if "data_summary" not in st.session_state:
    st.session_state.data_summary = None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SIDEBAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with st.sidebar:
    st.markdown("# 🧠 AI Data Analyst")
    st.markdown("*Upload · Ask · Discover*")
    st.divider()

    # ── API Configuration ───────────────────────────────────────────────
    st.markdown("### ⚙️ Configuration")

    # Initialize API key from .env on first load
    if "api_key_input" not in st.session_state:
        st.session_state.api_key_input = os.getenv("OPENROUTER_API_KEY", "")

    api_key = st.text_input(
        "OpenRouter API Key",
        type="password",
        key="api_key_input",
        help="Get your free key at https://openrouter.ai/keys",
    )

    selected_model_name = st.selectbox(
        "AI Model",
        options=list(OPENROUTER_MODELS.keys()),
        index=0,
        help="Choose which LLM to use for analysis",
    )
    selected_model = OPENROUTER_MODELS[selected_model_name]

    # Initialize or update LLM engine
    if api_key:
        if st.session_state.llm is None:
            st.session_state.llm = LLMEngine(api_key, selected_model)
        else:
            st.session_state.llm.client.api_key = api_key
            st.session_state.llm.set_model(selected_model)

    st.divider()

    # ── File Upload ─────────────────────────────────────────────────────
    st.markdown("### 📂 Upload Dataset")
    uploaded_file = st.file_uploader(
        "Drop your CSV file here",
        type=["csv"],
        help="Upload a CSV file to start analyzing",
    )

    if uploaded_file is not None:
        if st.session_state.df is None or uploaded_file.name != st.session_state.get("uploaded_filename"):
            with st.spinner("📊 Loading dataset..."):
                df = load_csv(uploaded_file)
                if df is not None:
                    st.session_state.df = df
                    st.session_state.uploaded_filename = uploaded_file.name
                    st.session_state.data_summary = get_data_summary(df)
                    st.session_state.messages = []  # Clear chat on new upload
                    if st.session_state.llm:
                        st.session_state.llm.clear_history()
                    st.success(f"✅ Loaded **{uploaded_file.name}** — {df.shape[0]} rows × {df.shape[1]} columns")

    # ── Dataset Preview ─────────────────────────────────────────────────
    if st.session_state.df is not None:
        st.divider()
        st.markdown("### 📋 Dataset Overview")
        summary = st.session_state.data_summary

        col1, col2 = st.columns(2)
        col1.metric("Rows", f"{summary['rows']:,}")
        col2.metric("Columns", summary['columns'])

        col3, col4 = st.columns(2)
        col3.metric("Numeric", len(summary['numeric_columns']))
        col4.metric("Categorical", len(summary['categorical_columns']))

        with st.expander("🔍 Column Details"):
            for col_name in summary['column_names']:
                dtype = summary['dtypes'][col_name]
                nulls = summary['null_counts'][col_name]
                null_pct = summary['null_percentage'][col_name]
                icon = "🔢" if col_name in summary['numeric_columns'] else "📝" if col_name in summary['categorical_columns'] else "📅"
                st.markdown(f"{icon} **{col_name}** `{dtype}` — {nulls} nulls ({null_pct}%)")

        with st.expander("👀 Preview Data"):
            st.dataframe(get_sample_rows(st.session_state.df, 10), use_container_width=True)

        # Clear chat button
        st.divider()
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            if st.session_state.llm:
                st.session_state.llm.clear_history()
            st.rerun()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MAIN CONTENT AREA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ── Welcome Screen (no data loaded) ────────────────────────────────────
if st.session_state.df is None:
    st.markdown("""
    <div style="text-align: center; padding: 80px 20px;">
        <h1 style="font-size: 3.5rem; font-weight: 700; 
            background: linear-gradient(135deg, #6C63FF, #FF6584, #43E97B);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 10px;">
            AI Data Analyst
        </h1>
        <p style="color: #8b949e; font-size: 1.3rem; margin-bottom: 40px;">
            Upload your data. Ask questions. Get insights instantly.
        </p>
        <div style="display: flex; justify-content: center; gap: 30px; flex-wrap: wrap;">
            <div style="background: rgba(22,27,34,0.6); backdrop-filter: blur(12px); border: 1px solid rgba(108,99,255,0.15);
                        border-radius: 20px; padding: 30px; width: 220px; text-align: center;">
                <div style="font-size: 2.5rem; margin-bottom: 10px;">📤</div>
                <h3 style="color: #c9d1d9; margin-bottom: 8px;">Upload</h3>
                <p style="color: #8b949e; font-size: 0.9rem;">Drop a CSV file in the sidebar</p>
            </div>
            <div style="background: rgba(22,27,34,0.6); backdrop-filter: blur(12px); border: 1px solid rgba(108,99,255,0.15);
                        border-radius: 20px; padding: 30px; width: 220px; text-align: center;">
                <div style="font-size: 2.5rem; margin-bottom: 10px;">💬</div>
                <h3 style="color: #c9d1d9; margin-bottom: 8px;">Ask</h3>
                <p style="color: #8b949e; font-size: 0.9rem;">Ask questions in plain English</p>
            </div>
            <div style="background: rgba(22,27,34,0.6); backdrop-filter: blur(12px); border: 1px solid rgba(108,99,255,0.15);
                        border-radius: 20px; padding: 30px; width: 220px; text-align: center;">
                <div style="font-size: 2.5rem; margin-bottom: 10px;">📊</div>
                <h3 style="color: #c9d1d9; margin-bottom: 8px;">Discover</h3>
                <p style="color: #8b949e; font-size: 0.9rem;">Get charts & insights</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ── Data is loaded — show main interface ────────────────────────────────
tab_chat, tab_explore = st.tabs(["💬 Chat with Data", "📊 Data Explorer"])


# ─────────────────────────────────────────────────────────────────────────
#  TAB 1: CHAT WITH DATA
# ─────────────────────────────────────────────────────────────────────────
with tab_chat:
    # Render existing messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "🧠"):
            st.markdown(message["content"])

            # Render stored chart if any
            if "figure" in message:
                st.plotly_chart(message["figure"], use_container_width=True)
            if "dataframe" in message:
                try:
                    st.dataframe(message["dataframe"], use_container_width=True)
                except Exception:
                    st.dataframe(message["dataframe"].astype(str), use_container_width=True)
            if "code" in message:
                with st.expander("🔍 View Generated Code"):
                    st.code(message["code"], language="python")

    # Suggested queries (only show when chat is empty)
    if not st.session_state.messages:
        st.markdown("#### 💡 Try asking:")
        suggestions = [
            "Show me a summary of the data",
            "What are the top 5 most common values?",
            "Create a bar chart of the main categories",
            "Are there any correlations between numeric columns?",
            "What trends do you see in the data?",
        ]
        cols = st.columns(len(suggestions))
        for i, suggestion in enumerate(suggestions):
            if cols[i].button(suggestion, key=f"suggest_{i}", use_container_width=True):
                st.session_state.pending_query = suggestion
                st.rerun()

    # Chat input
    query = st.chat_input("Ask anything about your data...")

    # Handle pending query from suggestions
    if "pending_query" in st.session_state:
        query = st.session_state.pending_query
        del st.session_state.pending_query

    if query:
        # Check prerequisites
        if not api_key:
            st.error("⚠️ Please enter your OpenRouter API key in the sidebar.")
            st.stop()
        if st.session_state.llm is None:
            st.error("⚠️ LLM engine not initialized. Check your API key.")
            st.stop()

        # Add user message
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(query)

        # Process with LLM
        with st.chat_message("assistant", avatar="🧠"):
            with st.spinner("🧠 Analyzing..."):
                dataset_info = format_dataframe_info(st.session_state.df)
                response = st.session_state.llm.generate_response(query, dataset_info)

            explanation = response.get("explanation", "")
            code = response.get("code", "")
            resp_type = response.get("type", "insight")

            message_data = {"role": "assistant", "content": explanation}

            st.markdown(explanation)

            # Execute code if present
            if code:
                with st.expander("🔍 View Generated Code"):
                    st.code(code, language="python")
                message_data["code"] = code

                with st.spinner("⚡ Executing..."):
                    result = execute_code(code, st.session_state.df)

                if result["success"]:
                    res = result["result"]

                    # Display based on result type
                    if hasattr(res, "update_layout"):
                        # Plotly figure
                        st.plotly_chart(res, use_container_width=True)
                        message_data["figure"] = res
                    elif isinstance(res, pd.DataFrame):
                        try:
                            st.dataframe(res, use_container_width=True)
                        except Exception:
                            st.dataframe(res.astype(str), use_container_width=True)
                        message_data["dataframe"] = res
                    elif isinstance(res, str):
                        st.markdown(res)
                        message_data["content"] = explanation + "\n\n" + res
                    else:
                        st.markdown(f"**Result:** `{res}`")
                        message_data["content"] = explanation + f"\n\n**Result:** `{res}`"
                else:
                    st.error(f"❌ Execution Error: {result['error']}")
                    message_data["content"] = explanation + f"\n\n❌ Error: {result['error']}"

            st.session_state.messages.append(message_data)


# ─────────────────────────────────────────────────────────────────────────
#  TAB 2: DATA EXPLORER
# ─────────────────────────────────────────────────────────────────────────
with tab_explore:
    st.markdown("### 📊 Automated Exploratory Data Analysis")
    st.markdown("Auto-generated visualizations for quick dataset understanding.")
    st.divider()

    eda_charts = quick_eda(st.session_state.df)

    for i in range(0, len(eda_charts), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(eda_charts):
                title, fig = eda_charts[idx]
                with col:
                    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.markdown("### 📋 Full Dataset")
    st.dataframe(st.session_state.df, use_container_width=True, height=400)

    # Download button
    csv_data = st.session_state.df.to_csv(index=False)
    st.download_button(
        "📥 Download CSV",
        csv_data,
        file_name="data_export.csv",
        mime="text/csv",
        use_container_width=True,
    )


