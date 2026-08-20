# 🎓 EduSense AI — AI-Powered Personalized Learning & Student Intelligence SaaS Platform

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.2+-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Tests Pass](https://img.shields.io/badge/Pytest-39%2F39%20Passed-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)

---

## 🌟 Overview

**EduSense AI** is a production-grade, end-to-end AI-powered personalized learning platform. It combines machine learning struggle risk classification, TF-IDF content recommendation engines, topological adaptive learning path generators, Socratic LLM conversational tutoring, dynamic AI quiz generation with closed-loop updates, and HuggingFace NLP feedback sentiment analysis into a cohesive SaaS application.

---

## 🚀 Key Platform Features

- 🧠 **Struggle Risk Prediction**: Evaluates student struggle risk across 3 models (**PyTorch Deep MLP Neural Net**, **Random Forest**, **Baseline Logistic Regression**) with real-time risk factor diagnosis.
- 🎯 **Content Recommendation Engine**: Vectorizes curriculum concepts via TF-IDF & Cosine Similarity, enforcing prerequisite graphs to generate explainable top-N recommendations.
- 🗺️ **Adaptive Personalization & Learning Paths**: Generates ordered DAG curriculum paths, tracking student performance trends and scaling difficulty automatically (`easy` ↔ `medium` ↔ `hard`).
- 💬 **NLP Student Feedback Analyzer**: Extracts student sentiment polarity, subjectivity, and thematic feedback tags using TextBlob & HuggingFace Transformers.
- 🤖 **Context-Aware Socratic LLM Tutor**: Integrates Ollama local LLM (`edusense-socratic-v1` fallback AI) injecting learner struggle risk diagnosis and prerequisite graphs.
- 📝 **AI Quiz Generator & Closed Learning Loop**: Dynamically constructs 4-option MCQs and executes automated closed-loop updates across DB records, predictions, profiles, and path completion statuses upon quiz submission.
- 🔐 **Production Backend Hardening**: JWT Bearer token authentication, salted password hashing, sliding-window IP rate limiting, `X-Request-ID` tracking headers, and custom exception envelopes.
- 🐳 **Docker & Compose Infrastructure**: Multi-stage production `Dockerfile`, Streamlit `Dockerfile.frontend`, and `docker-compose.yml` service orchestration.

---

## 🏗️ System Architecture

```
                      +----------------------------------+
                      | Streamlit Interactive Dashboard  |
                      |          (Port 8501)             |
                      +----------------+-----------------+
                                       |
                                       v
                      +----------------+-----------------+
                      |     FastAPI Backend Gateway      |
                      |  JWT Auth | Rate Limit | Req ID |
                      +----------------+-----------------+
                                       |
       +-------------------------------+-------------------------------+
       |                               |                               |
       v                               v                               v
+--------------+               +---------------+               +---------------+
| ML Prediction|               | Recommendation|               | LLM Tutor &   |
| Engine       |               | & Paths       |               | NLP Engine    |
| (PyTorch/RF) |               | (TF-IDF / DAG)|               | (Socratic AI) |
+--------------+               +---------------+               +---------------+
       |                               |                               |
       +-------------------------------+-------------------------------+
                                       |
                                       v
                      +----------------+-----------------+
                      |  SQLAlchemy Database & Datasets |
                      |    (SQLite / RDS PostgreSQL)     |
                      +----------------------------------+
```

---

## ⚡ Quickstart Guide

### Option 1: One-Command Docker Compose Launch (Recommended)

```bash
# Clone repository
git clone https://github.com/your-username/EduSense_AI.git
cd EduSense_AI

# Build and start multi-container production stack
docker-compose up --build -d
```
Access points:
- **Streamlit Frontend**: `http://localhost:8501`
- **FastAPI OpenAPI Swagger**: `http://localhost:8000/docs`

---

### Option 2: Local Python Virtual Environment

1. **Create and Activate Virtual Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Initialize Database & Train Models**:
   ```bash
   # Initialize DB Schema
   python -c "from app.db.session import init_db; init_db()"

   # Train PyTorch Deep Learning Model
   PYTHONPATH=. python ml/training/train_pytorch_struggle_model.py
   ```

4. **Launch Application Servers**:
   ```bash
   # Terminal 1: FastAPI Backend Server
   PYTHONPATH=. uvicorn app.main:app --reload --port 8000

   # Terminal 2: Streamlit Dashboard UI
   streamlit run frontend/main.py --server.port 8501
   ```

---

## 🧪 Test Suite Execution

Run full automated test suite (39+ tests):
```bash
pytest -v
```

Run Docker setup verification:
```bash
python scripts/verify_docker_setup.py
```

---

## 📡 REST API Catalog

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `POST` | `/auth/register` | Register user account with hashed password | ❌ |
| `POST` | `/auth/login` | Authenticate credentials & issue JWT token | ❌ |
| `GET` | `/auth/me` | Fetch authenticated user profile | 🔒 Bearer |
| `POST` | `/predict/struggle` | Predict struggle risk (`pytorch_nn`, `random_forest`) | ❌ |
| `GET` | `/models` | Retrieve model metrics & benchmark comparison | ❌ |
| `GET` | `/students/{id}/recommendations` | Explainable top-N content recommendations | ❌ |
| `POST` | `/learning-path` | Generate topological DAG learning path | ❌ |
| `POST` | `/tutor/chat` | Context-aware Socratic LLM tutor guidance | ❌ |
| `POST` | `/quiz/generate` | Dynamic MCQ question generation | ❌ |
| `POST` | `/quiz/submit` | Evaluate quiz & trigger closed learning loop | ❌ |
| `POST` | `/feedback/analyze` | NLP sentiment & theme extraction | ❌ |
| `GET` | `/health` | Application & Database health check | ❌ |

---

## 📚 Documentation Links

- [System Architecture Specification](file:///Users/harishrobinh/Desktop/EduSense_AI/docs/ARCHITECTURE.md)
- [AWS Cloud Deployment Strategy](file:///Users/harishrobinh/Desktop/EduSense_AI/docs/DEPLOYMENT_AWS.md)
