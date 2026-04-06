# 🧠 AI Data Analyst

**Upload your data. Ask questions. Get insights instantly.**

AI Data Analyst is a web-based application that allows users to upload structured datasets (CSV format) and interact with them using natural language. The system leverages LLMs and Machine Learning models to generate insights, visualizations, and predictions.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-ff4b4b?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🎯 Problem & Solution

**Problem:** Non-technical users struggle to analyze datasets quickly, write queries, and extract insights.

**Solution:** Upload CSV files, ask questions in plain English, and receive insights, visualizations, and predictions — no coding required.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📤 **CSV Upload** | Drag & drop CSV files with auto-parsing |
| 💬 **Natural Language Chat** | Ask questions about your data in plain English |
| 📊 **Auto Visualizations** | Interactive Plotly charts generated from queries |
| 🧠 **AI Insights** | Powered by any LLM via OpenRouter |
| 🔄 **Context Awareness** | Follow-up questions remember prior conversation |
| 📊 **Auto EDA** | Automatic exploratory data analysis charts |
| 🎨 **Premium Dark UI** | Glassmorphism design with smooth animations |

---

## 🏗️ Architecture

```
User → Streamlit UI → Backend API
                  ↓
            Data Loader (Pandas) → DataFrame
                  ↓
            User Query → LLM Engine (OpenRouter)
                  ↓
            Generated Code → Execution Engine
                  ↓
         Results → Visualization (Plotly)
                  ↓
            Charts → Streamlit UI
```

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **Backend:** Python, Pandas, NumPy
- **AI:** OpenRouter (any LLM)
- **Visualization:** Plotly
- **Styling:** Custom CSS with glassmorphism

---

## 🚀 Installation

### Prerequisites
- Python 3.9+
- An OpenRouter API key ([Get one free](https://openrouter.ai/keys))

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-data-analyst.git
cd ai-data-analyst

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your OpenRouter API key

# Run the app
streamlit run app.py
```

---

## 📖 Usage

1. **Upload** a CSV file via the sidebar
2. **Configure** your API key and select a model
3. **Chat** — ask questions like:
   - "Show me a summary of the data"
   - "Create a bar chart of revenue by product"
   - "What's the correlation between price and rating?"
4. **Explore** — browse auto-generated EDA charts

---

## 📂 Project Structure

```
ai-data-analyst/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── .env.example            # Environment variables template
├── data/
│   └── sample_sales.csv    # Demo dataset
├── src/
│   ├── __init__.py
│   ├── data_loader.py      # CSV parsing & DataFrame management
│   ├── llm_engine.py       # OpenRouter LLM integration
│   ├── execution_engine.py # Safe code execution sandbox
│   ├── visualization.py    # Plotly chart generation
│   └── utils.py            # Shared utilities
└── assets/
    └── style.css           # Custom dark theme CSS
```

---

## 🔮 Future Enhancements

- [ ] Excel/SQL support
- [ ] Multi-agent system
- [ ] Interactive dashboards
- [ ] Voice queries
- [ ] Cloud deployment
- [ ] Export reports as PDF

---

## 📄 License

This project is licensed under the MIT License.
