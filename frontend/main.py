"""Streamlit dashboard entrypoint for EduSense AI SaaS Platform."""

import os
import json
import requests
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="EduSense AI — AI-Powered Personalized Learning SaaS",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Custom CSS for Premium Glassmorphism & Vibrant Aesthetic
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 50%, #0F172A 100%);
        color: #F8FAFC;
    }
    
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #818CF8 0%, #C084FC 50%, #F472B6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    
    .hero-subtitle {
        color: #94A3B8;
        font-size: 1.15rem;
        font-weight: 500;
        margin-bottom: 1.8rem;
    }
    
    .glass-card {
        background: rgba(30, 41, 59, 0.65);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
        margin-bottom: 1rem;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .glass-card:hover {
        border-color: rgba(129, 140, 248, 0.3);
    }
    
    .status-badge-healthy {
        background: linear-gradient(135deg, rgba(5, 150, 105, 0.2) 0%, rgba(16, 185, 129, 0.2) 100%);
        color: #34D399;
        border: 1px solid rgba(52, 211, 153, 0.3);
        padding: 4px 14px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    
    .status-badge-unhealthy {
        background: linear-gradient(135deg, rgba(220, 38, 38, 0.2) 0%, rgba(239, 68, 68, 0.2) 100%);
        color: #FCA5A5;
        border: 1px solid rgba(252, 165, 165, 0.3);
        padding: 4px 14px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }

    .feature-tag {
        background: rgba(99, 102, 241, 0.15);
        color: #A5B4FC;
        border: 1px solid rgba(165, 180, 252, 0.2);
        padding: 2px 10px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 6px;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0B0F19;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Button Polish */
    .stButton>button {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        color: #FFFFFF;
        font-weight: 600;
        border-radius: 10px;
        border: none;
        padding: 0.6rem 1.4rem;
        box-shadow: 0 4px 14px 0 rgba(79, 70, 229, 0.35);
        transition: all 0.2s ease;
    }

    .stButton>button:hover {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
        box-shadow: 0 6px 20px 0 rgba(99, 102, 241, 0.45);
        transform: translateY(-1px);
    }

    /* Metric cards customization */
    [data-testid="stMetricValue"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 800;
        color: #F1F5F9;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


def fetch_backend_health():
    """Fetch health status from FastAPI backend."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=3)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None


# Sidebar Navigation
with st.sidebar:
    st.image("https://img.icons8.com/isometric/96/graduation-cap.png", width=60)
    st.markdown("## 🎓 EduSense AI")
    st.caption("AI-Powered Adaptive Learning Platform")
    st.divider()

    st.markdown("#### 📍 Navigation")
    selected_page = st.radio(
        "Select View",
        [
            "🏠 Home & Overview",
            "📊 Student Analytics & Risk Diagnostic",
            "🎯 Smart Recommendations",
            "🗺️ Personalized Learning Paths",
            "💬 Student Feedback & Sentiment",
            "🤖 Socratic AI Personal Tutor",
            "✏️ Interactive AI Quiz Generator",
            "🔐 Account Security & Profile",
            "🐳 Platform Infrastructure",
        ],
    )
    st.divider()

    # System Status Panel
    st.markdown("#### ⚡ Infrastructure Status")
    health = fetch_backend_health()
    if health:
        st.markdown('Backend API: <span class="status-badge-healthy">Online</span>', unsafe_allow_html=True)
        st.caption(f"Environment: **{health.get('environment', 'production').upper()}**")
        st.caption(f"Database: **{health.get('database', {}).get('database_type', 'SQLite').upper()}** (Connected)")
    else:
        st.markdown('Backend API: <span class="status-badge-unhealthy">Offline / Connecting</span>', unsafe_allow_html=True)
        st.caption("Connect backend on port 8000")

# Main Header
st.markdown('<div class="hero-title">EduSense AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">Next-Generation AI-Driven Adaptive Learning & Student Intelligence Platform</div>',
    unsafe_allow_html=True,
)

if selected_page == "🏠 Home & Overview":
    # Top Stats Row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="Active Learners", value="500+", delta="Live Cohort")
    with col2:
        st.metric(label="Curriculum Topics", value="20 Core", delta="Prerequisite Graph")
    with col3:
        st.metric(label="Quiz Assessments", value="11,169", delta="Closed Loop")
    with col4:
        st.metric(label="AI Model Accuracy", value="66.94%", delta="PyTorch Deep MLP")

    st.divider()

    # Platform Feature Highlights Grid
    st.markdown("### 🌟 Intelligent Learning Modules")
    
    grid1, grid2, grid3 = st.columns(3)
    
    with grid1:
        st.markdown(
            """
            <div class="glass-card">
                <h4>🧠 Struggle Risk Predictor</h4>
                <p style="color: #94A3B8; font-size: 0.9rem;">
                    Identifies at-risk students before quizzes using Deep Neural Networks & Random Forest classifiers.
                </p>
                <span class="feature-tag">PyTorch NN</span>
                <span class="feature-tag">Random Forest</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with grid2:
        st.markdown(
            """
            <div class="glass-card">
                <h4>🎯 Content Recommendations</h4>
                <p style="color: #94A3B8; font-size: 0.9rem;">
                    Recommends target concepts tailored to weak topics via TF-IDF vector similarity & prerequisite graphs.
                </p>
                <span class="feature-tag">TF-IDF Vectorizer</span>
                <span class="feature-tag">Top-N Recs</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with grid3:
        st.markdown(
            """
            <div class="glass-card">
                <h4>🗺️ Adaptive Learning Paths</h4>
                <p style="color: #94A3B8; font-size: 0.9rem;">
                    Generates dynamic DAG learning paths that automatically scale difficulty based on score velocity.
                </p>
                <span class="feature-tag">Topological DAG</span>
                <span class="feature-tag">Adaptive Scaling</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    grid4, grid5, grid6 = st.columns(3)

    with grid4:
        st.markdown(
            """
            <div class="glass-card">
                <h4>🤖 Socratic AI Tutor</h4>
                <p style="color: #94A3B8; font-size: 0.9rem;">
                    Context-aware AI tutor offering step-by-step guidance without revealing direct answers.
                </p>
                <span class="feature-tag">LLM Provider</span>
                <span class="feature-tag">Socratic AI</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with grid5:
        st.markdown(
            """
            <div class="glass-card">
                <h4>✏️ Dynamic AI Quizzes</h4>
                <p style="color: #94A3B8; font-size: 0.9rem;">
                    Generates 4-option MCQs and triggers instant closed-loop updates across student profiles & predictions.
                </p>
                <span class="feature-tag">MCQ Engine</span>
                <span class="feature-tag">Closed Loop</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with grid6:
        st.markdown(
            """
            <div class="glass-card">
                <h4>💬 Student NLP Sentiment</h4>
                <p style="color: #94A3B8; font-size: 0.9rem;">
                    Analyzes qualitative student feedback using HuggingFace & TextBlob sentiment extractors.
                </p>
                <span class="feature-tag">TextBlob NLP</span>
                <span class="feature-tag">HuggingFace</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # Data Summary
    st.markdown("### 📊 Dataset & Model Architecture Summary")
    
    d1, d2 = st.columns(2)
    with d1:
        st.markdown("#### 📁 Processed Dataset Snapshot")
        eda_path = "ml/data/processed/eda_summary.json"
        if os.path.exists(eda_path):
            with open(eda_path, "r") as f:
                eda_data = json.load(f)

            st.write(f"- **Total Student Attempts**: `{eda_data.get('total_quiz_attempts', 11169):,}`")
            st.write(f"- **Struggle Threshold**: `Average Score < 65%`")
            st.write(f"- **Struggle Rate**: `{eda_data.get('overall_struggle_rate', 0.442) * 100:.1f}%`")
            st.write(f"- **Total Registered Students**: `{eda_data.get('total_students', 500)}`")
        else:
            st.info("Dataset summary available upon backend launch.")

    with d2:
        st.markdown("#### ⚡ AI Model Comparison Overview")
        comp_data = pd.DataFrame([
            {"Model": "🧠 PyTorch Deep MLP", "Accuracy": "66.94%", "ROC-AUC": "0.7193", "F1 Score": "0.6377"},
            {"Model": "🌲 Random Forest", "Accuracy": "65.43%", "ROC-AUC": "0.7018", "F1 Score": "0.6357"},
            {"Model": "📈 Logistic Regression", "Accuracy": "65.11%", "ROC-AUC": "0.7153", "F1 Score": "0.6374"},
        ])
        st.table(comp_data)


elif selected_page == "📊 Student Analytics & Risk Diagnostic":
    st.markdown("### 📊 Student Analytics & Struggle Risk Diagnostic")
    st.caption("Analyze learner performance, predict struggle probability using AI, and inspect diagnostic risk factors.")

    tab1, tab2, tab3 = st.tabs(["👤 Student Performance Profile", "🔮 Live Risk Predictor Simulator", "📊 Model Comparison Matrix"])

    with tab1:
        c1, c2 = st.columns([1, 2])
        with c1:
            student_id = st.number_input("Select Student ID (1 - 500)", min_value=1, max_value=500, value=1, step=1)
            model_choice = st.selectbox("Select Model Architecture", options=["pytorch_nn", "random_forest", "logistic_regression"], format_func=lambda x: {"random_forest": "🌲 Random Forest Classifier", "pytorch_nn": "🧠 PyTorch Neural Network (Deep MLP)", "logistic_regression": "📈 Baseline Logistic Regression"}[x])

        with c2:
            st.markdown("#### 📋 Diagnostic Risk Assessment")
            try:
                payload = {"student_id": int(student_id), "topic_id": 12, "model_type": model_choice}
                res = requests.post(f"{API_BASE_URL}/predict/struggle", json=payload, timeout=3)
                if res.status_code == 200:
                    data = res.json()
                    prob = data["struggle_probability"]
                    risk = data["risk_level"].upper()
                    
                    st.metric("Struggle Probability", f"{prob * 100:.1f}%", delta=f"Risk Level: {risk}")
                    
                    if data["is_struggling"]:
                        st.error(f"⚠️ **HIGH STRUGGLE RISK DETECTED** (Probability: {prob*100:.1f}%)")
                    else:
                        st.success(f"✅ **CONCEPT MASTERY LIKELY** (Probability: {prob*100:.1f}%)")

                    st.markdown("**Identified Risk Factors:**")
                    for factor in data.get("risk_factors", []):
                        st.markdown(f"- ⚠️ {factor}")
                else:
                    st.warning("Connect backend API to run live student predictions.")
            except Exception as e:
                st.info("Start FastAPI backend server to run live model predictions.")

    with tab2:
        st.markdown("#### 🔮 Custom Parameter Struggle Simulator")
        col_m = st.selectbox("Select Model Architecture for Simulation", options=["pytorch_nn", "random_forest", "logistic_regression"], format_func=lambda x: {"random_forest": "🌲 Random Forest", "pytorch_nn": "🧠 PyTorch Neural Network (Deep MLP)", "logistic_regression": "📈 Logistic Regression"}[x])
        col_a, col_b = st.columns(2)
        with col_a:
            recent_score = st.slider("Recent Quiz Average Score (%)", 0.0, 100.0, 58.0)
            hist_score = st.slider("Historical Subject Average Score (%)", 0.0, 100.0, 62.0)
            attempts = st.slider("Attempts on Target Topic", 1, 5, 2)
            time_spent = st.slider("Total Time Spent (seconds)", 30, 900, 420)

        with col_b:
            prereq_rate = st.slider("Prerequisite Mastery Rate (0.0 - 1.0)", 0.0, 1.0, 0.40)
            score_trend = st.slider("Score Trend Delta (Recent - Historical)", -30.0, 30.0, -4.0)
            engagement = st.slider("14-Day Engagement Frequency", 0, 30, 3)
            diff_num = st.selectbox("Topic Difficulty", options=[1, 2, 3], format_func=lambda x: {1: "Easy (1)", 2: "Medium (2)", 3: "Hard (3)"}[x], index=1)

        sim_payload = {
            "recent_quiz_score": float(recent_score),
            "historical_topic_score": float(hist_score),
            "attempts_count": int(attempts),
            "total_time_spent": int(time_spent),
            "prerequisite_completion_rate": float(prereq_rate),
            "score_trend": float(score_trend),
            "engagement_frequency": int(engagement),
            "topic_difficulty_numeric": int(diff_num),
            "model_type": col_m,
        }

        try:
            res = requests.post(f"{API_BASE_URL}/predict/struggle", json=sim_payload, timeout=3)
            if res.status_code == 200:
                out = res.json()
                st.divider()
                st.markdown(f"### Predicted Struggle Probability ({out.get('model_version', col_m)}): **{out['struggle_probability'] * 100:.1f}%**")
                st.info(f"Risk Category: **{out['risk_level'].upper()}** | Decision: {'Struggling (Intervention Suggested)' if out['is_struggling'] else 'Mastering'}")
                if out.get("risk_factors"):
                    st.markdown("**Key Risk Factors Detected:**")
                    for rf in out["risk_factors"]:
                        st.markdown(f"- ⚠️ {rf}")
        except Exception as ex:
            st.warning(f"FastAPI server offline for simulation: {ex}")

    with tab3:
        st.markdown("#### Deep Learning vs Classical ML Model Benchmarks")
        try:
            m_res = requests.get(f"{API_BASE_URL}/models", timeout=3)
            if m_res.status_code == 200:
                m_data = m_res.json()

                bm1, bm2, bm3 = st.columns(3)
                with bm1:
                    st.markdown("##### 🧠 PyTorch Deep Learning MLP")
                    pt_m = m_data.get("pytorch_nn", {"accuracy": 0.6694, "precision": 0.6844, "recall": 0.5969, "f1_score": 0.6377, "roc_auc": 0.7193})
                    st.metric("Accuracy", f"{pt_m['accuracy']*100:.2f}%")
                    st.write(f"- **Precision**: {pt_m['precision']:.4f}")
                    st.write(f"- **Recall**: {pt_m['recall']:.4f}")
                    st.write(f"- **F1-Score**: {pt_m['f1_score']:.4f}")
                    st.write(f"- **ROC-AUC**: {pt_m['roc_auc']:.4f}")

                with bm2:
                    st.markdown("##### 🌲 Random Forest Classifier")
                    rf_m = m_data.get("random_forest", m_data.get("metrics_test", {"accuracy": 0.6543, "precision": 0.6535, "recall": 0.6189, "f1_score": 0.6357, "roc_auc": 0.7018}))
                    st.metric("Accuracy", f"{rf_m['accuracy']*100:.2f}%")
                    st.write(f"- **Precision**: {rf_m['precision']:.4f}")
                    st.write(f"- **Recall**: {rf_m['recall']:.4f}")
                    st.write(f"- **F1-Score**: {rf_m['f1_score']:.4f}")
                    st.write(f"- **ROC-AUC**: {rf_m['roc_auc']:.4f}")

                with bm3:
                    st.markdown("##### 📈 Logistic Regression")
                    lr_m = m_data.get("logistic_regression", m_data.get("metrics_baseline_logistic_regression", {"accuracy": 0.6511, "precision": 0.6459, "recall": 0.6292, "f1_score": 0.6374, "roc_auc": 0.7153}))
                    st.metric("Accuracy", f"{lr_m['accuracy']*100:.2f}%")
                    st.write(f"- **Precision**: {lr_m['precision']:.4f}")
                    st.write(f"- **Recall**: {lr_m['recall']:.4f}")
                    st.write(f"- **F1-Score**: {lr_m['f1_score']:.4f}")
                    st.write(f"- **ROC-AUC**: {lr_m['roc_auc']:.4f}")

                st.divider()
                st.markdown("##### 💡 Model Comparison Matrix:")
                comp_df = pd.DataFrame([
                    {"Model": "🧠 PyTorch Deep MLP", "Accuracy (%)": pt_m['accuracy']*100, "Precision": pt_m['precision'], "Recall": pt_m['recall'], "F1 Score": pt_m['f1_score'], "ROC-AUC": pt_m['roc_auc']},
                    {"Model": "🌲 Random Forest", "Accuracy (%)": rf_m['accuracy']*100, "Precision": rf_m['precision'], "Recall": rf_m['recall'], "F1 Score": rf_m['f1_score'], "ROC-AUC": rf_m['roc_auc']},
                    {"Model": "📈 Logistic Regression", "Accuracy (%)": lr_m['accuracy']*100, "Precision": lr_m['precision'], "Recall": lr_m['recall'], "F1 Score": lr_m['f1_score'], "ROC-AUC": lr_m['roc_auc']},
                ])
                st.dataframe(comp_df, use_container_width=True)
        except Exception as e:
            st.info("Start FastAPI backend to inspect live model evaluation benchmarks.")


elif selected_page == "🎯 Smart Recommendations":
    st.markdown("### 🎯 Content-Based Topic Recommendations & Prerequisite Filtering")
    st.caption("Identify weak topics, calculate TF-IDF concept similarity, and generate explainable top-N recommendations.")

    rec_c1, rec_c2 = st.columns([1, 1])
    with rec_c1:
        rec_student_id = st.number_input("Select Student ID", min_value=1, max_value=500, value=1, step=1, key="rec_sid")
    with rec_c2:
        top_n = st.slider("Number of Recommendations (Top-N)", min_value=1, max_value=10, value=3)

    if st.button("🚀 Fetch Top-N Recommendations", type="primary"):
        try:
            res = requests.get(f"{API_BASE_URL}/students/{rec_student_id}/recommendations?top_n={top_n}", timeout=5)
            if res.status_code == 200:
                rec_data = res.json()
                st.divider()
                st.markdown(f"#### 🎯 Recommended Topics for Student #{rec_data['student_id']}:")

                for idx, rec in enumerate(rec_data["recommendations"]):
                    with st.expander(f"#{idx+1}: {rec['topic_name']} ({rec['subject']}) — Match Score: {rec['recommendation_score']*100:.1f}%", expanded=(idx==0)):
                        st.markdown(f"**Difficulty**: `{rec['difficulty'].title()}` | **Prerequisites Met**: {'✅ Yes' if rec['prerequisites_met'] else '⚠️ No'}")
                        st.info(f"💡 Explanation: {rec['explanation']}")
            else:
                st.error(f"API Error ({res.status_code}): {res.text}")
        except Exception as e:
            st.error(f"Could not reach recommendations API: {e}")


elif selected_page == "🔐 Account Security & Profile":
    st.markdown("### 🔐 User Account Authentication & Security")
    st.caption("JWT bearer token authentication, salted password hashing, rate limiting, and request tracking headers.")

    tab_sec1, tab_sec2, tab_sec3 = st.tabs(["🔑 Sign In / Register", "👤 Authenticated Profile (/auth/me)", "🛡️ Security Middleware Status"])

    with tab_sec1:
        s_c1, s_c2 = st.columns(2)
        with s_c1:
            st.markdown("#### 📝 Register New Account")
            r_name = st.text_input("Full Name", value="Alex Johnson", key="r_name")
            r_email = st.text_input("Email Address", value="alex@example.com", key="r_email")
            r_pass = st.text_input("Password", type="password", value="SecretPass123!", key="r_pass")
            r_role = st.selectbox("Account Role", options=["student", "instructor"], key="r_role")

            if st.button("🚀 Create Account & Issue Token", type="primary"):
                try:
                    payload = {"name": r_name, "email": r_email, "password": r_pass, "role": r_role}
                    reg_res = requests.post(f"{API_BASE_URL}/auth/register", json=payload, timeout=5)
                    if reg_res.status_code in (200, 201):
                        out_reg = reg_res.json()
                        st.session_state["jwt_token"] = out_reg["access_token"]
                        st.success(f"Account created successfully for {out_reg['name']}! JWT Token stored.")
                        st.json(out_reg)
                    else:
                        st.error(f"Registration Failed: {reg_res.text}")
                except Exception as ex:
                    st.error(f"API Error: {ex}")

        with s_c2:
            st.markdown("#### 🔐 Sign In to Existing Account")
            l_email = st.text_input("Email Address", value="alex@example.com", key="l_email")
            l_pass = st.text_input("Password", type="password", value="SecretPass123!", key="l_pass")

            if st.button("🔑 Log In & Authenticate", type="primary"):
                try:
                    l_payload = {"email": l_email, "password": l_pass}
                    log_res = requests.post(f"{API_BASE_URL}/auth/login", json=l_payload, timeout=5)
                    if log_res.status_code == 200:
                        out_log = log_res.json()
                        st.session_state["jwt_token"] = out_log["access_token"]
                        st.success(f"Successfully logged in as {out_log['name']}!")
                        st.json(out_log)
                    else:
                        st.error(f"Login Failed: {log_res.text}")
                except Exception as ex:
                    st.error(f"API Error: {ex}")

    with tab_sec2:
        st.markdown("#### 👤 Protected Profile Lookup (`GET /auth/me`)")
        tok = st.session_state.get("jwt_token", "")
        token_input = st.text_area("Bearer Token", value=tok, height=80)

        if st.button("🔍 Inspect Authenticated User Profile"):
            if not token_input:
                st.warning("Please register or log in first to issue a Bearer token.")
            else:
                try:
                    headers = {"Authorization": f"Bearer {token_input}"}
                    me_res = requests.get(f"{API_BASE_URL}/auth/me", headers=headers, timeout=5)
                    if me_res.status_code == 200:
                        st.success("Successfully authenticated with JWT token!")
                        st.json(me_res.json())
                    else:
                        st.error(f"Authentication Failed ({me_res.status_code}): {me_res.text}")
                except Exception as ex:
                    st.error(f"API Request Error: {ex}")

    with tab_sec3:
        st.markdown("#### 🛡️ Production Security Protection Status")
        st.markdown(
            """
            - **X-Request-ID Injection**: Every API response includes a unique distributed tracking UUID header.
            - **Sliding-Window IP Rate Limiter**: 120 requests per minute per IP limit (`429 Too Many Requests`).
            - **CORS Protection**: Access restricted to configured trusted origins.
            - **Salted Password Hashing**: PBKDF2/SHA256 with 100,000 iterations and random salt.
            """
        )


elif selected_page == "🐳 Platform Infrastructure":
    st.markdown("### 🐳 Container Infrastructure & Topology")
    st.caption("Multi-stage production Dockerfiles, docker-compose topology, persistent data volumes, and healthchecks.")

    d_c1, d_c2 = st.columns(2)
    with d_c1:
        st.markdown("#### 📦 Docker Container Topology")
        st.markdown(
            """
            - **`edusense_backend`**:
              - **Base Image**: `python:3.11-slim` (Multi-stage build)
              - **Exposed Port**: `8000`
              - **Healthcheck**: `curl -f http://localhost:8000/health`
              - **User**: `appuser` (Non-root security)
              - **Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2`
            - **`edusense_frontend`**:
              - **Base Image**: `python:3.11-slim`
              - **Exposed Port**: `8501`
              - **Healthcheck**: `curl -f http://localhost:8501/_stcore/health`
              - **Env**: `API_BASE_URL=http://backend:8000`
              - **Command**: `streamlit run frontend/main.py`
            - **`edusense_data` Volume**:
              - Shared persistent volume mounting `/app/edusense.db` and `/app/ml/artifacts`.
            """
        )

    with d_c2:
        st.markdown("#### ⚡ Infrastructure Status")
        if os.path.exists("Dockerfile") and os.path.exists("docker-compose.yml"):
            st.success("✅ Dockerfile & docker-compose.yml verified in project root!")
            st.info("Run `docker-compose up --build -d` to launch containers in production mode.")
        else:
            st.warning("Docker files missing.")

        with st.expander("📄 View docker-compose.yml Specification"):
            if os.path.exists("docker-compose.yml"):
                with open("docker-compose.yml", "r") as f:
                    st.code(f.read(), language="yaml")


elif selected_page == "✏️ Interactive AI Quiz Generator":
    st.markdown("### ✏️ Dynamic AI Quiz Generator & Closed Learning Loop")
    st.caption("Generate dynamic MCQs, take quizzes, and trigger automatic closed-loop updates across learner profiles, predictions, and paths.")

    qz_c1, qz_c2, qz_c3 = st.columns([1, 1, 1])
    with qz_c1:
        qz_student_id = st.number_input("Select Student ID", min_value=1, max_value=500, value=1, step=1, key="qz_sid")
    with qz_c2:
        qz_topic_id = st.number_input("Target Topic ID (1 - 20)", min_value=1, max_value=20, value=12, step=1, key="qz_tid")
    with qz_c3:
        q_count = st.slider("Number of Questions", min_value=1, max_value=5, value=3)

    if st.button("⚡ Generate Dynamic Quiz", type="primary"):
        try:
            gen_res = requests.post(f"{API_BASE_URL}/quiz/generate", json={"student_id": int(qz_student_id), "topic_id": int(qz_topic_id), "question_count": int(q_count)}, timeout=5)
            if gen_res.status_code == 200:
                st.session_state["active_quiz"] = gen_res.json()
                st.success("Dynamic Quiz generated successfully! Answer the questions below.")
            else:
                st.error(f"API Error: {gen_res.text}")
        except Exception as e:
            st.error(f"Could not generate quiz: {e}")

    active_q = st.session_state.get("active_quiz")
    if active_q:
        st.divider()
        st.markdown(f"#### 📖 Quiz: **{active_q['topic_name']}** ({active_q['subject']})")
        st.caption(f"Session ID: `{active_q['quiz_session_id']}` | Difficulty: **{active_q['difficulty'].title()}**")

        user_choices = []
        for idx, q in enumerate(active_q["questions"]):
            st.markdown(f"**Q{idx+1}: {q['question_text']}**")
            choice = st.radio(f"Select option for Q{idx+1}", options=q["options"], index=0, key=f"q_choice_{idx}")
            user_choices.append(q["options"].index(choice))

        if st.button("📤 Submit Quiz Answers & Run Closed Loop", type="primary"):
            try:
                sub_payload = {
                    "student_id": int(active_q["student_id"]),
                    "topic_id": int(active_q["topic_id"]),
                    "quiz_session_id": active_q["quiz_session_id"],
                    "answers": user_choices,
                    "time_spent": 180,
                }
                sub_res = requests.post(f"{API_BASE_URL}/quiz/submit", json=sub_payload, timeout=8)
                if sub_res.status_code == 200:
                    out = sub_res.json()
                    st.divider()

                    # Header Results Banner
                    s_pct = out["score_percentage"]
                    pass_badge = "🟢 PASSED" if out["is_passed"] else "🔴 NEEDS REVIEW"
                    st.markdown(f"## Quiz Score: **{s_pct:.1f}%** ({out['correct_answers']}/{out['total_questions']} Correct) — {pass_badge}")

                    # Closed Loop Updates Visualizer
                    st.markdown("#### 🔄 Closed Learning Loop Automated Updates:")
                    cl = out["closed_loop_updates"]

                    cl_1, cl_2, cl_3, cl_4 = st.columns(4)
                    with cl_1:
                        st.metric("Attempt DB Record", "SAVED ✅")
                    with cl_2:
                        st.metric("Struggle Risk Level", cl["struggle_risk_level"].upper(), delta=f"{cl['struggle_probability']*100:.1f}% prob")
                    with cl_3:
                        st.metric("Adaptive Difficulty", cl["new_difficulty"].title(), delta="SCALED" if cl["difficulty_changed"] else None)
                    with cl_4:
                        st.metric("Path Completion", f"{cl['learning_path_completion_pct']}%")

                    if cl["difficulty_changed"]:
                        st.balloons()
                        st.warning(f"⚡ **CLOSED-LOOP TRIGGER**: {cl['adaptive_reason']}")

                    st.markdown("#### 📋 Question Breakdown & Explanations:")
                    for qb in out["question_breakdown"]:
                        q_status = "✅ Correct" if qb["is_correct"] else "❌ Incorrect"
                        with st.expander(f"Q{qb['question_id']}: {q_status}"):
                            st.write(f"**Question**: {qb['question_text']}")
                            st.write(f"**Your Answer**: `{qb['user_selected_option']}`")
                            if not qb["is_correct"]:
                                st.write(f"**Correct Answer**: `{qb['correct_option_text']}`")
                            st.info(f"💡 Explanation: {qb['explanation']}")
                else:
                    st.error(f"API Error: {sub_res.text}")
            except Exception as ex:
                st.error(f"Could not submit quiz: {ex}")


elif selected_page == "🤖 Socratic AI Personal Tutor":
    st.markdown("### 🤖 Socratic AI Personal Tutor")
    st.caption("Context-aware AI tutor leveraging student struggle risk, weak topics, and prerequisite graphs for step-by-step guidance.")

    t_c1, t_c2 = st.columns([1, 1])
    with t_c1:
        tut_student_id = st.number_input("Select Student ID", min_value=1, max_value=500, value=1, step=1, key="tut_sid")
    with t_c2:
        tut_topic_id = st.number_input("Target Topic ID (1 - 20)", min_value=1, max_value=20, value=12, step=1, key="tut_tid")

    # Load initial student tutor history or context
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    st.markdown("**Quick Socratic Prompts:**")
    prompt_cols = st.columns(3)
    with prompt_cols[0]:
        if st.button("💡 I don't understand this concept"):
            st.session_state["user_prompt"] = "I am struggling to understand this topic. Can you explain the core intuitions step-by-step?"
    with prompt_cols[1]:
        if st.button("❓ Give me a guiding question"):
            st.session_state["user_prompt"] = "Don't give me the direct solution. Ask me a Socratic guiding question to test my understanding."
    with prompt_cols[2]:
        if st.button("🔗 What are the prerequisites?"):
            st.session_state["user_prompt"] = "What foundational topics do I need to review before mastering this concept?"

    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask your Socratic AI Tutor a question...", key="chat_input")
    active_prompt = user_input or st.session_state.pop("user_prompt", None)

    if active_prompt:
        st.session_state["messages"].append({"role": "user", "content": active_prompt})
        with st.chat_message("user"):
            st.markdown(active_prompt)

        try:
            tut_payload = {
                "student_id": int(tut_student_id),
                "topic_id": int(tut_topic_id),
                "message": active_prompt,
            }
            res = requests.post(f"{API_BASE_URL}/tutor/chat", json=tut_payload, timeout=8)
            if res.status_code in (200, 201):
                tut_data = res.json()
                tutor_reply = tut_data["reply"]

                with st.chat_message("assistant"):
                    st.markdown(tutor_reply)
                    st.caption(f"🤖 Powered by `{tut_data['provider']}` ({tut_data['model_used']}) | Risk Diagnosis: **{tut_data['struggle_risk_level'].upper()} RISK**")

                st.session_state["messages"].append({"role": "assistant", "content": tutor_reply})
            else:
                st.error(f"API Error: {res.text}")
        except Exception as e:
            st.error(f"Could not reach LLM Tutor backend: {e}")


elif selected_page == "🗺️ Personalized Learning Paths":
    st.markdown("### 🗺️ Adaptive Learning Paths & Skill Progression")
    st.caption("Topologically sorted step-by-step curriculum paths enforcing prerequisite mastery and dynamic difficulty adaptation.")

    tab1, tab2 = st.tabs(["🛣️ Learning Path Visualizer", "📝 Interactive Quiz & Adaptive Difficulty Tester"])

    with tab1:
        c1, c2 = st.columns([2, 1])
        with c1:
            lp_student_id = st.number_input("Select Student ID", min_value=1, max_value=500, value=1, step=1, key="lp_sid")
        with c2:
            target_sub = st.selectbox("Filter Target Subject", options=["All Subjects", "Machine Learning", "Deep Learning & NLP", "Python Programming", "Mathematics for ML"])

        if st.button("🚀 Generate / Refresh Learning Path", type="primary"):
            try:
                sub_param = None if target_sub == "All Subjects" else target_sub
                res = requests.post(f"{API_BASE_URL}/learning-path", json={"student_id": int(lp_student_id), "target_subject": sub_param}, timeout=5)
                if res.status_code in (200, 201):
                    lp_data = res.json()
                    st.divider()

                    # Progress Header Metrics
                    m1, m2, m3, m4 = st.columns(4)
                    with m1:
                        st.metric("Target Goal", lp_data["target_goal"])
                    with m2:
                        st.metric("Completion Rate", f"{lp_data['completion_percentage']}%", delta=f"{lp_data['completed_steps']}/{lp_data['total_steps']} steps")
                    with m3:
                        st.metric("Estimated Time", f"{lp_data['estimated_total_hours']} hrs")
                    with m4:
                        st.metric("Adaptive Difficulty", lp_data['current_preferred_difficulty'].title())

                    st.progress(float(lp_data['completion_percentage']) / 100.0)

                    st.markdown("#### 📌 Step-by-Step Curriculum Sequence (Topological Order):")

                    for step in lp_data["steps"]:
                        st_icon = "✅" if step["status"] == "completed" else ("🔄" if step["status"] == "in_progress" else "🔒")

                        with st.expander(f"{st_icon} Step {step['step_number']}: {step['topic_name']} ({step['difficulty'].title()}) — {step['status'].upper()}", expanded=(step["status"] == "in_progress")):
                            cl, cr = st.columns([3, 1])
                            with cl:
                                st.markdown(f"**Subject**: `{step['subject']}`")
                                if step["prerequisites"]:
                                    st.caption(f"Prerequisites: {', '.join(step['prerequisites'])}")
                                else:
                                    st.caption("Prerequisites: None (Foundational Topic)")
                            with cr:
                                st.write(f"⏱️ **Est. Time**: {step['estimated_minutes']} mins")
                                if step["best_score"] is not None:
                                    st.write(f"🏆 **Best Score**: {step['best_score']}%")
                else:
                    st.error(f"API Error: {res.text}")
            except Exception as e:
                st.error(f"Could not generate learning path: {e}")

    with tab2:
        st.markdown("#### Simulate Quiz Attempt & Test Real-time Adaptive Scaling")
        st.caption("Submit test quiz scores to trigger automated difficulty adjustments in student profile.")

        q_c1, q_c2 = st.columns(2)
        with q_c1:
            q_sid = st.number_input("Student ID", min_value=1, max_value=500, value=1, step=1, key="q_sid")
            q_tid = st.number_input("Topic ID (1 - 20)", min_value=1, max_value=20, value=12, step=1, key="q_tid")
        with q_c2:
            q_score = st.slider("Quiz Score (%)", 0.0, 100.0, 95.0, step=1.0)
            q_time = st.number_input("Time Spent (seconds)", min_value=30, max_value=1800, value=300, step=30)

        if st.button("📤 Submit Quiz Attempt & Update Profile", type="primary"):
            try:
                q_payload = {
                    "student_id": int(q_sid),
                    "topic_id": int(q_tid),
                    "score": float(q_score),
                    "time_spent": int(q_time),
                }
                q_res = requests.post(f"{API_BASE_URL}/quiz-attempts", json=q_payload, timeout=5)
                if q_res.status_code in (200, 201):
                    q_data = q_res.json()
                    st.divider()
                    st.success(f"Quiz attempt submitted successfully for {q_data['topic_name']}!")

                    r_col1, r_col2 = st.columns(2)
                    with r_col1:
                        st.metric("Recorded Score", f"{q_data['score']}%")
                        st.metric("Previous Difficulty", q_data["previous_difficulty"].title())
                    with r_col2:
                        st.metric("Attempt #", q_data["attempt_number"])
                        st.metric("New Difficulty", q_data["new_difficulty"].title(), delta="UPDATED" if q_data["difficulty_changed"] else None)

                    if q_data["difficulty_changed"]:
                        st.balloons()
                        st.warning(f"🎉 **ADAPTIVE DIFFICULTY UPDATE**: {q_data['adaptive_reason']}")
                    else:
                        st.info(f"ℹ️ {q_data['adaptive_reason']}")
                else:
                    st.error(f"API Error: {q_res.text}")
            except Exception as ex:
                st.error(f"Could not submit quiz attempt: {ex}")


elif selected_page == "💬 Student Feedback & Sentiment":
    st.markdown("### 💬 Student Feedback & Sentiment Analysis")
    st.caption("Extract student sentiment polarity, detect friction topics, and extract key learning themes from text comments.")

    tab1, tab2 = st.tabs(["📝 Submit & Analyze Feedback", "📈 Student Sentiment Analytics Dashboard"])

    with tab1:
        f_c1, f_c2 = st.columns([1, 1])
        with f_c1:
            fb_student_id = st.number_input("Select Student ID", min_value=1, max_value=500, value=1, step=1, key="fb_sid")
        with f_c2:
            fb_topic_id = st.number_input("Target Topic ID (Optional, 1 - 20)", min_value=1, max_value=20, value=12, step=1, key="fb_tid")

        st.markdown("**Quick Preset Sample Comments:**")
        preset_cols = st.columns(3)
        with preset_cols[0]:
            if st.button("🟢 Positive Preset"):
                st.session_state["fb_text"] = "The explanation of logistic regression was clear, helpful, and very informative!"
        with preset_cols[1]:
            if st.button("⚪ Neutral Preset"):
                st.session_state["fb_text"] = "Completed the practice problems. Need more examples."
        with preset_cols[2]:
            if st.button("🔴 Negative Preset"):
                st.session_state["fb_text"] = "I felt confused, frustrated, and stuck on the difficult calculus derivatives!"

        fb_input_text = st.text_area("Enter Student Comment / Feedback", value=st.session_state.get("fb_text", "The explanation of logistic regression was clear, helpful, and very informative!"), height=100)

        if st.button("🔍 Analyze Sentiment & Save Feedback", type="primary"):
            try:
                fb_payload = {
                    "student_id": int(fb_student_id),
                    "topic_id": int(fb_topic_id) if fb_topic_id else None,
                    "text": fb_input_text,
                }
                res = requests.post(f"{API_BASE_URL}/feedback/analyze", json=fb_payload, timeout=5)
                if res.status_code in (200, 201):
                    data = res.json()
                    st.divider()

                    s_score = data["sentiment_score"]
                    s_label = data["sentiment_label"].upper()
                    s_icon = "🟢" if s_label == "POSITIVE" else ("🔴" if s_label == "NEGATIVE" else "⚪")

                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.metric("Sentiment Label", f"{s_icon} {s_label}")
                    with m2:
                        st.metric("Polarity Score", f"{s_score:+.2f}")
                    with m3:
                        st.metric("Feedback Entry ID", f"#{data['feedback_id']}")

                    st.markdown("#### 🏷️ Detected Friction Themes & Tags:")
                    for theme in data.get("extracted_themes", []):
                        st.markdown(f"- 📌 **{theme['theme'].title()}**: {theme['description']}")
                else:
                    st.error(f"API Error: {res.text}")
            except Exception as e:
                st.error(f"Could not analyze feedback: {e}")

    with tab2:
        st.markdown("#### 📈 Student Sentiment Overview")
        try:
            res = requests.get(f"{API_BASE_URL}/students/1/sentiment", timeout=3)
            if res.status_code == 200:
                s_data = res.json()
                st.write(f"- **Total Submissions**: `{s_data.get('total_feedback_entries', 5)}`")
                st.write(f"- **Average Sentiment Polarity**: `{s_data.get('average_polarity', 0.25):+.2f}`")
                st.write(f"- **Dominant Tone**: `{s_data.get('dominant_sentiment', 'Positive').upper()}`")
            else:
                st.info("Start FastAPI backend server to load live student sentiment analytics.")
        except Exception:
            st.info("Start FastAPI backend server to load live student sentiment analytics.")
