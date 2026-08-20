# 🎓 EduSense AI — Version 1.0.0 Release Notes

**Release Version:** `v1.0.0`  
**Release Date:** August 20, 2026  
**Status:** Production Ready & Live Deployed  
**Repository:** [github.com/harishrobin11/EduSense_AI](https://github.com/harishrobin11/EduSense_AI)  
**Live Application:** [edusense-ai-frontend.onrender.com](https://edusense-ai-frontend.onrender.com)  
**API Documentation:** [edusense-ai-api.onrender.com/docs](https://edusense-ai-api.onrender.com/docs)  

---

## 🌟 Executive Summary

**EduSense AI v1.0.0** is the initial major production release of an AI-Powered Personalised Learning & Student Intelligence SaaS Platform. EduSense AI continuously predicts student struggle risks, dynamically adapts learning path difficulties, generates explainable content recommendations, coaches students via a Socratic LLM tutor, and maintains real-time closed-loop updates across student profiles.

---

## 🚀 Key Modules & Features

### 1. 🧠 Struggle Risk Diagnostic & Early Intervention Engine
- **PyTorch Deep MLP Neural Network**: Multi-layer perceptron trained on synthetic educational data to detect student struggle probability before quiz attempts.
- **Ensemble Benchmarking**: Includes PyTorch Deep MLP (66.94% Accuracy, 0.7193 ROC-AUC), Random Forest (65.43% Accuracy), and Logistic Regression baselines.
- **Custom Parameter Simulator**: Interactive UI tool for simulating risk levels across 8 custom student performance metrics.

### 2. 🎯 Smart Recommendation Engine
- **TF-IDF Vector Similarity**: Content-based recommendation matching student weak topics with relevant learning modules.
- **Prerequisite Filtering**: Enforces topic dependency graphs to prevent recommending advanced material before foundational concepts are mastered.
- **Top-N Explainability**: Provides natural language explanations for every recommendation.

### 3. 🗺️ Adaptive Learning Paths & DAG Topology
- **Topological Sequence**: Converts prerequisite graphs into step-by-step curriculum sequences.
- **Dynamic Difficulty Scaling**: Automatically scales difficulty (`easy` ➔ `medium` ➔ `hard`) based on score velocity and historical progress.
- **Progress Tracking**: Tracks step status (`completed`, `in_progress`, `locked`) and score achievements.

### 4. 🤖 Socratic AI Personal Tutor
- **Step-by-Step Guidance**: Context-aware AI coach using the Socratic method to ask guiding questions rather than giving away direct solutions.
- **Risk-Aware Prompting**: Automatically adapts conversation style based on the student's current struggle risk level.

### 5. ✏️ Interactive AI Quiz & Closed Learning Loop
- **Dynamic MCQ Generation**: Generates 4-option multiple choice questions tailored to topic difficulty.
- **Closed Loop Automated Updates**: Submitting a quiz instantly updates attempt records, struggle probabilities, adaptive difficulty levels, and learning path progress.

### 6. 💬 Student Feedback NLP & Sentiment Friction Detection
- **Sentiment Polarity Extraction**: Uses TextBlob & HuggingFace pipelines to analyze qualitative student comments.
- **Friction Topic Identification**: Detects negative sentiment patterns to alert instructors of problematic curriculum topics.

### 7. 🔐 Production Backend Hardening & Security
- **Authentication**: Signed JWT tokens (`HS256`) with salted `PBKDF2/SHA-256` password hashing (100,000 iterations).
- **Security Middleware**: Sliding-window IP rate limiting (120 req/min), CORS origin restriction, and unique `X-Request-ID` UUID response headers.

### 8. 🐳 Infrastructure & Multi-Container Cloud Deployment
- **Docker Architecture**: Multi-stage production `Dockerfile` (backend) and lightweight `Dockerfile.frontend`.
- **Render.com Cloud Blueprint**: Automated Infrastructure-as-Code (`render.yaml`) orchestrating FastAPI backend and Streamlit frontend web services.

---

## 📊 Model Evaluation Benchmarks

| Model Architecture | Accuracy | Precision | Recall | F1 Score | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 🧠 **PyTorch Deep MLP** | **66.94%** | **0.6844** | 0.5969 | **0.6377** | **0.7193** |
| 🌲 **Random Forest Classifier** | 65.43% | 0.6535 | 0.6189 | 0.6357 | 0.7018 |
| 📈 **Logistic Regression Baseline** | 65.11% | 0.6459 | **0.6292** | 0.6374 | 0.7153 |

---

## 🛠️ Technology Stack

- **Backend Framework**: Python 3.11, FastAPI, Uvicorn, Pydantic v2
- **Database Layer**: SQLite, SQLAlchemy ORM
- **Machine Learning & NLP**: PyTorch, Scikit-learn, Pandas, NumPy, TextBlob
- **Security**: PyJWT, Passlib (PBKDF2-SHA256), Cryptography
- **Frontend Dashboard**: Streamlit, Custom Dark Glassmorphism CSS, Space Grotesk & Inter Typography
- **Containerization & Deployment**: Docker, Docker Compose, Render Blueprint (`render.yaml`)

---

## 📡 Core API Endpoints

- `GET /health` — Service health & database connectivity
- `POST /predict/struggle` — Struggle risk prediction
- `GET /students/{student_id}/recommendations` — Smart topic recommendations
- `POST /learning-path` — Generate adaptive topological learning path
- `POST /quiz/generate` — Dynamic MCQ quiz generator
- `POST /quiz/submit` — Submit quiz & trigger closed-loop updates
- `POST /tutor/chat` — Socratic AI tutor conversation
- `POST /feedback/analyze` — Student feedback NLP sentiment analysis
- `POST /auth/register` & `POST /auth/login` — Account management & JWT issuing
- `GET /auth/me` — Protected user profile inspection

---

## 👥 Authors & License

- **Developer**: Harish Robin ([@harishrobin11](https://github.com/harishrobin11))
- **License**: MIT License
