# 🧠 Enterprise AI Data Analyst Platform

**Enterprise-grade AI-powered data analytics platform. Upload files, auto-clean, run statistical models, forecast trends, train machine learning predictors, and chat using a true multi-agent system.**

---

## 🏗️ Architecture

```
                       +----------------------------------+
                       |       Next.js 15 Frontend        |
                       | (React 19, TypeScript, Recharts) |
                       +----------------+-----------------+
                                        | HTTPS / SSE
                                        v
                       +----------------+-----------------+
                       |        FastAPI Backend           |
                       |       (Python & SQLAlchemy)      |
                       +-------+--------+--------+--------+
                               |        |        |
             +-----------------+        |        +-----------------+
             | DuckDB Engine            | Celery Task              | Redis cache
             v                          v                          v
+------------+------------+   +---------+---------+   +------------+------------+
|  Local SQLite Fallback  |   |   Celery Workers  |   |      Redis Broker       |
|      Metadata Storage   |   |   (Polars Core)   |   |      & Task Queue       |
+-------------------------+   +---------+---------+   +-------------------------+
                                        |
                                        v
                              +---------+---------+
                              | Multi-Agent System|
                              | (Planner, Cleaner |
                              | EDA, ML, Stats,   |
                              | Insight, Visual)  |
                              +-------------------+
```

---

## ✨ Features

- **True Multi-Agent Orchestration**: A `PlannerAgent` coordinates specialized worker agents (`cleaner`, `eda`, `stats`, `ml`, `forecaster`, `visualizer`, `insight`) via schema-enforced structured JSON.
- **Fast Data Diagnostics**: Powered by **Polars** (lazy evaluations) and **DuckDB** local queries for lightning-fast metrics calculation.
- **Auto Data Cleaning**: Detects null parameters, indexes duplicate records, flags statistical outliers using Interquartile Range boundaries, and suggests database column name refactoring.
- **Hypothesis Testing & Forecasts**: Runs standard Chi-Square tests, t-tests, ANOVA, and time series projection models on dates aggregates.
- **Secure Sandboxed Interpreter**: Local Python sandbox executing generated scripts using whitelisted functions, modules, and built-ins.
- **Premium Dark Minimalist UI**: Sleek workspace featuring workspace switchers, datasets preview tables, chat threads, and custom settings panel.

---

## 📂 Monorepo Structure

```text
ai-data-analyst/
├── backend/                  # FastAPI Application
│   ├── app/
│   │   ├── api/              # CRUD endpoints (auth, projects, datasets, chats, dashboards)
│   │   ├── core/             # config, database, security, celery_app
│   │   ├── models/           # SQLAlchemy Database models (User, Project, Dataset, Chat, Dashboard)
│   │   ├── schemas/          # Pydantic serialization models
│   │   ├── services/         # file_service, execution_service (sandbox)
│   │   └── agents/           # Multi-agent implementations
│   └── tests/                # Pytest unit coverage
├── frontend/                 # Next.js 15 + React 19 Frontend
│   ├── app/                  # Route layouts and global stylesheets
│   └── components/           # Dashboard, ChatInterface, DataExplorer, VisualizationStudio, SettingsPanel
├── docker/                   # Orchestrations
│   └── docker-compose.yml
└── README.md
```

---

## 🚀 Getting Started

### Local Setup (Manual)

#### 1. Backend

1. Navigate to the backend folder:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables in `.env` (copy from `.env.example` in root or backend):
   ```ini
   OPENROUTER_API_KEY=your-api-key
   DEFAULT_MODEL=google/gemini-2.0-flash-exp:free
   ```
5. Run the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

#### 2. Frontend

1. Navigate to the frontend folder:
   ```bash
   cd ../frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Run the Next.js development server:
   ```bash
   npm run dev
   ```
4. Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🐳 Docker Deployment

1. Run the entire container stack (Redis, FastAPI Backend, Next.js Frontend, Celery worker) from the `docker` directory:
   ```bash
   cd docker
   docker-compose up --build
   ```
2. The frontend is accessible on `http://localhost:3000` and the backend documentation is on `http://localhost:8000/docs`.
