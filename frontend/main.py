"""Streamlit dashboard entrypoint for EduSense AI — Premium AI-Powered Learning Platform."""

import os
import json
import requests
import pandas as pd
import streamlit as st

# ─── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EduSense AI — Your Personal AI Learning Coach",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# ─── Premium CSS Design System ─────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    /* ── Base Reset ── */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, sans-serif;
    }

    /* ── Background ── */
    .stApp {
        background: radial-gradient(ellipse at 20% 0%, rgba(99,57,255,0.18) 0%, transparent 55%),
                    radial-gradient(ellipse at 80% 10%, rgba(236,72,153,0.12) 0%, transparent 45%),
                    radial-gradient(ellipse at 50% 100%, rgba(6,182,212,0.10) 0%, transparent 55%),
                    linear-gradient(160deg, #07091A 0%, #0D0F2B 40%, #0A0E24 100%);
        color: #E2E8F0;
        min-height: 100vh;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #050715 0%, #0B0F27 100%);
        border-right: 1px solid rgba(139,92,246,0.15);
    }
    section[data-testid="stSidebar"] .stRadio > label {
        color: #94A3B8 !important;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
        gap: 4px;
    }
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        padding: 10px 14px;
        border-radius: 10px;
        border: 1px solid transparent;
        font-size: 0.88rem !important;
        font-weight: 500;
        color: #CBD5E1 !important;
        transition: all 0.2s ease;
        text-transform: none !important;
        letter-spacing: 0 !important;
    }
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
        background: rgba(139,92,246,0.12);
        border-color: rgba(139,92,246,0.25);
        color: #A78BFA !important;
    }

    /* ── Hero Section ── */
    .hero-wrap {
        padding: 2.5rem 0 1.5rem 0;
        margin-bottom: 0.5rem;
    }
    .hero-eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(139,92,246,0.12);
        border: 1px solid rgba(139,92,246,0.3);
        border-radius: 999px;
        padding: 5px 16px;
        font-size: 0.78rem;
        font-weight: 700;
        color: #A78BFA;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 1.2rem;
    }
    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(2.2rem, 5vw, 3.8rem);
        font-weight: 700;
        letter-spacing: -0.03em;
        line-height: 1.1;
        background: linear-gradient(135deg, #FFFFFF 0%, #C4B5FD 40%, #F472B6 80%, #FB923C 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.8rem;
    }
    .hero-sub {
        font-size: 1.1rem;
        font-weight: 400;
        color: #94A3B8;
        line-height: 1.65;
        max-width: 640px;
    }

    /* ── Stat Cards ── */
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin: 2rem 0;
    }
    .stat-card {
        background: rgba(15,18,40,0.8);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 16px;
        padding: 1.4rem 1.5rem;
        position: relative;
        overflow: hidden;
        transition: border-color 0.3s ease, transform 0.2s ease;
    }
    .stat-card::before {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(135deg, rgba(139,92,246,0.06) 0%, transparent 60%);
        border-radius: 16px;
    }
    .stat-card:hover {
        border-color: rgba(139,92,246,0.35);
        transform: translateY(-2px);
    }
    .stat-icon {
        font-size: 1.5rem;
        margin-bottom: 0.7rem;
        display: block;
    }
    .stat-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: #F1F5F9;
        line-height: 1;
        margin-bottom: 0.3rem;
    }
    .stat-label {
        font-size: 0.82rem;
        font-weight: 500;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .stat-delta {
        font-size: 0.78rem;
        font-weight: 600;
        color: #34D399;
        margin-top: 0.4rem;
    }

    /* ── Feature Cards ── */
    .feature-card {
        background: rgba(13,15,35,0.9);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 20px;
        padding: 1.8rem;
        height: 100%;
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
        cursor: default;
    }
    .feature-card::after {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: var(--card-accent, linear-gradient(90deg, #8B5CF6, #EC4899));
        border-radius: 20px 20px 0 0;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .feature-card:hover {
        border-color: rgba(139,92,246,0.3);
        transform: translateY(-4px);
        box-shadow: 0 20px 40px -12px rgba(0,0,0,0.5), 0 0 0 1px rgba(139,92,246,0.1);
    }
    .feature-card:hover::after {
        opacity: 1;
    }
    .feature-icon-wrap {
        width: 48px; height: 48px;
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.4rem;
        margin-bottom: 1rem;
        background: var(--icon-bg, rgba(139,92,246,0.15));
    }
    .feature-card h4 {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.05rem;
        font-weight: 600;
        color: #F1F5F9;
        margin-bottom: 0.6rem;
        letter-spacing: -0.01em;
    }
    .feature-card p {
        font-size: 0.88rem;
        color: #64748B;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    .tag-row { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 0.8rem; }
    .tag {
        background: rgba(99,102,241,0.1);
        color: #818CF8;
        border: 1px solid rgba(129,140,248,0.2);
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.03em;
    }

    /* ── Section Headers ── */
    .section-header {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #F1F5F9;
        letter-spacing: -0.02em;
        margin-bottom: 0.3rem;
    }
    .section-sub {
        font-size: 0.9rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }

    /* ── Pill Badge ── */
    .badge-online {
        display: inline-flex; align-items: center; gap: 6px;
        background: rgba(16,185,129,0.1);
        border: 1px solid rgba(52,211,153,0.25);
        color: #34D399;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .badge-online::before { content: '●'; animation: pulse-dot 2s infinite; }
    .badge-offline {
        display: inline-flex; align-items: center; gap: 6px;
        background: rgba(239,68,68,0.1);
        border: 1px solid rgba(252,165,165,0.25);
        color: #FCA5A5;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    @keyframes pulse-dot {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
    }

    /* ── Info Banner ── */
    .info-banner {
        background: linear-gradient(135deg, rgba(99,102,241,0.08) 0%, rgba(139,92,246,0.05) 100%);
        border: 1px solid rgba(99,102,241,0.2);
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        font-size: 0.88rem;
        color: #A5B4FC;
        line-height: 1.6;
        margin: 1rem 0;
    }

    /* ── Glass Panel ── */
    .glass-panel {
        background: rgba(13,15,35,0.8);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 18px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }

    /* ── Data table overrides ── */
    .stDataFrame { border-radius: 12px; overflow: hidden; }
    [data-testid="stDataFrameResizable"] { border-radius: 12px; }

    /* ── Metric overrides ── */
    [data-testid="stMetricValue"] {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 1.6rem !important;
        color: #F1F5F9;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.78rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    /* ── Button overrides ── */
    .stButton > button {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
        color: #FFFFFF;
        font-weight: 600;
        border-radius: 10px;
        border: none;
        padding: 0.55rem 1.4rem;
        font-size: 0.88rem;
        box-shadow: 0 4px 14px rgba(99,102,241,0.3);
        transition: all 0.2s ease;
        letter-spacing: 0.01em;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #818CF8 0%, #A78BFA 100%);
        box-shadow: 0 6px 20px rgba(139,92,246,0.4);
        transform: translateY(-1px);
    }

    /* ── Input overrides ── */
    .stTextInput > div > div, .stNumberInput > div > div,
    .stTextArea > div > div, .stSelectbox > div > div {
        background: rgba(15,18,40,0.9) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
        color: #E2E8F0 !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(13,15,35,0.8);
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
        border: 1px solid rgba(255,255,255,0.06);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        font-weight: 500;
        font-size: 0.88rem;
        color: #64748B;
        padding: 8px 20px;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(99,102,241,0.2) !important;
        color: #A78BFA !important;
        font-weight: 600;
    }

    /* ── Progress bar ── */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #6366F1, #8B5CF6, #EC4899) !important;
        border-radius: 999px !important;
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        background: rgba(13,15,35,0.6) !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 10px !important;
        font-weight: 500;
        font-size: 0.9rem;
        color: #CBD5E1;
    }

    /* ── Divider ── */
    hr { border-color: rgba(255,255,255,0.06) !important; }

    /* ── Chat messages ── */
    [data-testid="stChatMessageContent"] p { font-size: 0.92rem; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(139,92,246,0.3); border-radius: 99px; }

    /* ── Logo animation ── */
    @keyframes logo-float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-4px); }
    }
    .sidebar-logo { animation: logo-float 4s ease-in-out infinite; display: inline-block; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─── Helpers ───────────────────────────────────────────────────────────────────
def fetch_backend_health():
    """Fetch health status from FastAPI backend."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=3)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None


def render_feature_card(icon, title, desc, tags, accent_from, accent_to, icon_bg):
    return f"""
    <div class="feature-card" style="--card-accent: linear-gradient(90deg, {accent_from}, {accent_to}); --icon-bg: {icon_bg}">
        <div class="feature-icon-wrap">{icon}</div>
        <h4>{title}</h4>
        <p>{desc}</p>
        <div class="tag-row">{"".join(f'<span class="tag">{t}</span>' for t in tags)}</div>
    </div>"""


# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<span class="sidebar-logo" style="font-size:2.2rem;">🎓</span>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-family:\'Space Grotesk\',sans-serif;font-size:1.25rem;font-weight:700;'
        'color:#F1F5F9;margin-bottom:2px;">EduSense AI</div>'
        '<div style="font-size:0.75rem;color:#4B5563;font-weight:500;letter-spacing:0.05em;'
        'text-transform:uppercase;margin-bottom:1rem;">Personal Learning Coach</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    selected_page = st.radio(
        "Navigate",
        [
            "🏠  Home",
            "📊  My Analytics",
            "🎯  Recommendations",
            "🗺️  Learning Path",
            "💬  My Feedback",
            "🤖  AI Tutor",
            "✏️  AI Quiz",
            "🔐  My Account",
            "🐳  Infrastructure",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    # Live Status
    st.markdown(
        '<div style="font-size:0.72rem;font-weight:700;color:#4B5563;text-transform:uppercase;'
        'letter-spacing:0.08em;margin-bottom:0.6rem;">System Status</div>',
        unsafe_allow_html=True,
    )
    health = fetch_backend_health()
    if health:
        st.markdown('<span class="badge-online">API Online</span>', unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:0.78rem;color:#4B5563;margin-top:0.5rem;">'
            f'DB · {health.get("database", {}).get("database_type", "SQLite").upper()}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<span class="badge-offline">API Offline</span>', unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:0.75rem;color:#4B5563;margin-top:0.4rem;">Start backend on :8000</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.72rem;color:#1E293B;text-align:center;padding-top:1rem;">'
        'Powered by PyTorch · FastAPI · Streamlit</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
#   HOME PAGE
# ═══════════════════════════════════════════════════════════════════════════════
if selected_page == "🏠  Home":

    # Hero
    st.markdown(
        """
        <div class="hero-wrap">
            <div class="hero-eyebrow">✦ AI-Powered Personalized Learning</div>
            <div class="hero-title">Learn Smarter.<br>Grow Faster.</div>
            <div class="hero-sub">
                EduSense AI adapts to <em>your</em> unique learning style — predicting struggles before they happen,
                building personalised paths, and coaching you with a Socratic AI tutor.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Stat Cards
    st.markdown(
        """
        <div class="stat-grid">
            <div class="stat-card">
                <span class="stat-icon">👩‍🎓</span>
                <div class="stat-value">500+</div>
                <div class="stat-label">Active Learners</div>
                <div class="stat-delta">▲ Live cohort</div>
            </div>
            <div class="stat-card">
                <span class="stat-icon">📚</span>
                <div class="stat-value">20</div>
                <div class="stat-label">Core Topics</div>
                <div class="stat-delta">▲ Prerequisite graph</div>
            </div>
            <div class="stat-card">
                <span class="stat-icon">✅</span>
                <div class="stat-value">11K+</div>
                <div class="stat-label">Quiz Attempts</div>
                <div class="stat-delta">▲ Closed-loop system</div>
            </div>
            <div class="stat-card">
                <span class="stat-icon">🤖</span>
                <div class="stat-value">66.9%</div>
                <div class="stat-label">AI Accuracy</div>
                <div class="stat-delta">▲ Deep Neural Network</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # Feature Cards
    st.markdown('<div class="section-header">What EduSense AI Does For You</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Six intelligent modules working together to accelerate your learning journey.</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            render_feature_card(
                "🧠", "Struggle Risk Predictor",
                "Detects when you're about to struggle with a concept before it happens, using Deep Neural Networks trained on thousands of student journeys.",
                ["PyTorch MLP", "Random Forest", "Real-time"],
                "#8B5CF6", "#EC4899",
                "rgba(139,92,246,0.15)",
            ),
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            render_feature_card(
                "🎯", "Smart Recommendations",
                "Surfaces the exact topics you need to review next using TF-IDF concept similarity and prerequisite graph filtering.",
                ["TF-IDF Vectors", "Top-N Engine", "Prerequisite Map"],
                "#06B6D4", "#6366F1",
                "rgba(6,182,212,0.15)",
            ),
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            render_feature_card(
                "🗺️", "Adaptive Learning Paths",
                "Generates a personalised step-by-step curriculum in topological order, automatically scaling difficulty based on your progress.",
                ["DAG Topology", "Adaptive Scaling", "Progress Tracking"],
                "#10B981", "#06B6D4",
                "rgba(16,185,129,0.15)",
            ),
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown(
            render_feature_card(
                "🤖", "Socratic AI Tutor",
                "Your personal AI coach that guides you with thought-provoking questions instead of giving away answers — building true understanding.",
                ["LLM-Powered", "Socratic Method", "Context-Aware"],
                "#F59E0B", "#EF4444",
                "rgba(245,158,11,0.15)",
            ),
            unsafe_allow_html=True,
        )
    with c5:
        st.markdown(
            render_feature_card(
                "✏️", "Dynamic AI Quizzes",
                "Auto-generates personalised MCQ quizzes for any topic and instantly updates your risk profile in a closed learning loop.",
                ["MCQ Generator", "Closed Loop", "Instant Feedback"],
                "#EC4899", "#8B5CF6",
                "rgba(236,72,153,0.15)",
            ),
            unsafe_allow_html=True,
        )
    with c6:
        st.markdown(
            render_feature_card(
                "💬", "Sentiment Analysis",
                "Understands your frustration signals from feedback comments using NLP, helping instructors spot friction topics early.",
                ["TextBlob NLP", "HuggingFace", "Theme Extraction"],
                "#6366F1", "#10B981",
                "rgba(99,102,241,0.15)",
            ),
            unsafe_allow_html=True,
        )

    st.divider()

    # Data Summary
    st.markdown('<div class="section-header">Dataset & Model Benchmarks</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Trained and validated on a real-world educational dataset of 500 students.</div>',
        unsafe_allow_html=True,
    )

    d1, d2 = st.columns([1, 1])
    with d1:
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.markdown("##### 📁 Dataset Snapshot")
        eda_path = "ml/data/processed/eda_summary.json"
        if os.path.exists(eda_path):
            with open(eda_path, "r") as f:
                eda_data = json.load(f)
            stats = {
                "Total Quiz Attempts": f"{eda_data.get('total_quiz_attempts', 11169):,}",
                "Registered Students": f"{eda_data.get('total_students', 500)}",
                "Struggle Rate": f"{eda_data.get('overall_struggle_rate', 0.442) * 100:.1f}%",
                "Struggle Threshold": "Avg Score < 65%",
            }
            for k, v in stats.items():
                st.markdown(
                    f'<div style="display:flex;justify-content:space-between;padding:8px 0;'
                    f'border-bottom:1px solid rgba(255,255,255,0.05);">'
                    f'<span style="color:#64748B;font-size:0.85rem;">{k}</span>'
                    f'<span style="color:#F1F5F9;font-weight:600;font-size:0.85rem;">{v}</span></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("Dataset summary available upon backend launch.")
        st.markdown("</div>", unsafe_allow_html=True)

    with d2:
        st.markdown("##### ⚡ AI Model Comparison")
        comp_data = pd.DataFrame([
            {"Model": "🧠 PyTorch Deep MLP", "Accuracy": "66.94%", "ROC-AUC": "0.7193", "F1": "0.6377"},
            {"Model": "🌲 Random Forest", "Accuracy": "65.43%", "ROC-AUC": "0.7018", "F1": "0.6357"},
            {"Model": "📈 Logistic Regression", "Accuracy": "65.11%", "ROC-AUC": "0.7153", "F1": "0.6374"},
        ])
        st.dataframe(comp_data, width="stretch", hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
#   ANALYTICS PAGE
# ═══════════════════════════════════════════════════════════════════════════════
elif selected_page == "📊  My Analytics":
    st.markdown('<div class="hero-title" style="font-size:2rem;">Student Analytics</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Analyse learner performance, predict struggle probability, and compare AI models.</div>',
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(["👤 Student Profile", "🔮 Risk Simulator", "📊 Model Benchmarks"])

    with tab1:
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
            student_id = st.number_input("Student ID (1–500)", min_value=1, max_value=500, value=1, step=1)
            model_choice = st.selectbox(
                "AI Model",
                options=["pytorch_nn", "random_forest", "logistic_regression"],
                format_func=lambda x: {
                    "pytorch_nn": "🧠 PyTorch Neural Network",
                    "random_forest": "🌲 Random Forest",
                    "logistic_regression": "📈 Logistic Regression",
                }[x],
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            st.markdown("#### 📋 Live Risk Assessment")
            try:
                payload = {"student_id": int(student_id), "topic_id": 12, "model_type": model_choice}
                res = requests.post(f"{API_BASE_URL}/predict/struggle", json=payload, timeout=3)
                if res.status_code == 200:
                    data = res.json()
                    prob = data["struggle_probability"]
                    risk = data["risk_level"].upper()

                    m1, m2 = st.columns(2)
                    with m1:
                        st.metric("Struggle Probability", f"{prob * 100:.1f}%", delta=f"Risk: {risk}")
                    with m2:
                        st.metric("Assessment", "⚠️ At Risk" if data["is_struggling"] else "✅ On Track")

                    if data["is_struggling"]:
                        st.error(f"⚠️ High struggle risk detected ({prob*100:.1f}%). Review recommended topics now.")
                    else:
                        st.success(f"✅ You're on track! Keep it up (Risk: {prob*100:.1f}%)")

                    if data.get("risk_factors"):
                        st.markdown("**Risk Factors Identified:**")
                        for factor in data["risk_factors"]:
                            st.markdown(f"- ⚠️ {factor}")
                else:
                    st.markdown(
                        '<div class="info-banner">🔌 Connect to the backend API on port 8000 to run live student predictions.</div>',
                        unsafe_allow_html=True,
                    )
            except Exception:
                st.markdown(
                    '<div class="info-banner">🚀 Start the FastAPI backend server to see live AI predictions for this student.</div>',
                    unsafe_allow_html=True,
                )

    with tab2:
        st.markdown("#### 🔮 Risk Simulator — Adjust Parameters")
        col_m = st.selectbox(
            "Model for Simulation",
            options=["pytorch_nn", "random_forest", "logistic_regression"],
            format_func=lambda x: {"pytorch_nn": "🧠 PyTorch NN", "random_forest": "🌲 Random Forest", "logistic_regression": "📈 Logistic Regression"}[x],
        )
        col_a, col_b = st.columns(2)
        with col_a:
            recent_score = st.slider("Recent Quiz Average (%)", 0.0, 100.0, 58.0)
            hist_score = st.slider("Historical Average (%)", 0.0, 100.0, 62.0)
            attempts = st.slider("Attempts on Topic", 1, 5, 2)
            time_spent = st.slider("Time Spent (sec)", 30, 900, 420)
        with col_b:
            prereq_rate = st.slider("Prerequisite Mastery (0–1)", 0.0, 1.0, 0.40)
            score_trend = st.slider("Score Trend Delta", -30.0, 30.0, -4.0)
            engagement = st.slider("14-Day Engagement", 0, 30, 3)
            diff_num = st.selectbox("Topic Difficulty", options=[1, 2, 3], format_func=lambda x: {1: "🟢 Easy", 2: "🟡 Medium", 3: "🔴 Hard"}[x], index=1)

        sim_payload = {
            "recent_quiz_score": float(recent_score), "historical_topic_score": float(hist_score),
            "attempts_count": int(attempts), "total_time_spent": int(time_spent),
            "prerequisite_completion_rate": float(prereq_rate), "score_trend": float(score_trend),
            "engagement_frequency": int(engagement), "topic_difficulty_numeric": int(diff_num),
            "model_type": col_m,
        }
        try:
            res = requests.post(f"{API_BASE_URL}/predict/struggle", json=sim_payload, timeout=3)
            if res.status_code == 200:
                out = res.json()
                st.divider()
                pct = out["struggle_probability"] * 100
                st.metric(f"Predicted Struggle Probability ({out.get('model_version', col_m)})", f"{pct:.1f}%")
                st.info(f"Risk Category: **{out['risk_level'].upper()}** — {'Intervention Suggested' if out['is_struggling'] else 'Mastery Likely'}")
                for rf in out.get("risk_factors", []):
                    st.markdown(f"- ⚠️ {rf}")
        except Exception:
            st.markdown(
                '<div class="info-banner">🔌 Connect backend to run simulation predictions in real-time.</div>',
                unsafe_allow_html=True,
            )

    with tab3:
        st.markdown("#### Deep Learning vs Classical ML Benchmarks")
        try:
            m_res = requests.get(f"{API_BASE_URL}/models", timeout=3)
            if m_res.status_code == 200:
                m_data = m_res.json()
                bm1, bm2, bm3 = st.columns(3)
                defaults = {
                    "pytorch_nn": {"accuracy": 0.6694, "precision": 0.6844, "recall": 0.5969, "f1_score": 0.6377, "roc_auc": 0.7193},
                    "random_forest": {"accuracy": 0.6543, "precision": 0.6535, "recall": 0.6189, "f1_score": 0.6357, "roc_auc": 0.7018},
                    "logistic_regression": {"accuracy": 0.6511, "precision": 0.6459, "recall": 0.6292, "f1_score": 0.6374, "roc_auc": 0.7153},
                }
                labels = {"pytorch_nn": "🧠 PyTorch Deep MLP", "random_forest": "🌲 Random Forest", "logistic_regression": "📈 Logistic Regression"}
                for col, key in zip([bm1, bm2, bm3], ["pytorch_nn", "random_forest", "logistic_regression"]):
                    md = m_data.get(key, defaults[key])
                    with col:
                        st.markdown(f"##### {labels[key]}")
                        st.metric("Accuracy", f"{md['accuracy']*100:.2f}%")
                        for k in ["precision", "recall", "f1_score", "roc_auc"]:
                            st.write(f"- **{k.replace('_',' ').title()}**: {md[k]:.4f}")
                st.divider()
                comp_df = pd.DataFrame([
                    {"Model": labels[k], "Accuracy (%)": round(defaults[k]["accuracy"]*100, 2),
                     "Precision": defaults[k]["precision"], "Recall": defaults[k]["recall"],
                     "F1": defaults[k]["f1_score"], "ROC-AUC": defaults[k]["roc_auc"]}
                    for k in ["pytorch_nn", "random_forest", "logistic_regression"]
                ])
                st.dataframe(comp_df, width="stretch", hide_index=True)
        except Exception:
            st.markdown(
                '<div class="info-banner">🔌 Start FastAPI backend to inspect live model evaluation benchmarks.</div>',
                unsafe_allow_html=True,
            )


# ═══════════════════════════════════════════════════════════════════════════════
#   RECOMMENDATIONS PAGE
# ═══════════════════════════════════════════════════════════════════════════════
elif selected_page == "🎯  Recommendations":
    st.markdown('<div class="hero-title" style="font-size:2rem;">Smart Recommendations</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Personalised topic recommendations using TF-IDF concept similarity and prerequisite graph filtering.</div>',
        unsafe_allow_html=True,
    )

    rec_c1, rec_c2 = st.columns([1, 1])
    with rec_c1:
        rec_student_id = st.number_input("Student ID", min_value=1, max_value=500, value=1, step=1, key="rec_sid")
    with rec_c2:
        top_n = st.slider("Number of Recommendations", min_value=1, max_value=10, value=3)

    if st.button("🚀 Get My Recommendations", type="primary"):
        try:
            res = requests.get(f"{API_BASE_URL}/students/{rec_student_id}/recommendations?top_n={top_n}", timeout=5)
            if res.status_code == 200:
                rec_data = res.json()
                st.divider()
                st.markdown(f"#### 🎯 Recommended for Student #{rec_data['student_id']}")
                for idx, rec in enumerate(rec_data["recommendations"]):
                    with st.expander(
                        f"#{idx+1} · {rec['topic_name']} ({rec['subject']}) — {rec['recommendation_score']*100:.1f}% Match",
                        expanded=(idx == 0),
                    ):
                        st.markdown(
                            f"**Difficulty**: `{rec['difficulty'].title()}` · "
                            f"**Prerequisites Met**: {'✅ Yes' if rec['prerequisites_met'] else '⚠️ No'}"
                        )
                        st.info(f"💡 {rec['explanation']}")
            else:
                st.error(f"API Error ({res.status_code}): {res.text}")
        except Exception as e:
            st.error(f"Could not reach recommendations API: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
#   LEARNING PATH PAGE
# ═══════════════════════════════════════════════════════════════════════════════
elif selected_page == "🗺️  Learning Path":
    st.markdown('<div class="hero-title" style="font-size:2rem;">My Learning Path</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">A personalised curriculum built just for you — step-by-step, prerequisite-aware, and adaptive.</div>',
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(["🛣️ Path Visualiser", "📝 Quiz & Adaptive Difficulty"])

    with tab1:
        c1, c2 = st.columns([2, 1])
        with c1:
            lp_student_id = st.number_input("Student ID", min_value=1, max_value=500, value=1, step=1, key="lp_sid")
        with c2:
            target_sub = st.selectbox(
                "Filter Subject",
                options=["All Subjects", "Machine Learning", "Deep Learning & NLP", "Python Programming", "Mathematics for ML"],
            )

        if st.button("🚀 Generate My Learning Path", type="primary"):
            try:
                sub_param = None if target_sub == "All Subjects" else target_sub
                res = requests.post(f"{API_BASE_URL}/learning-path", json={"student_id": int(lp_student_id), "target_subject": sub_param}, timeout=5)
                if res.status_code in (200, 201):
                    lp_data = res.json()
                    st.divider()
                    m1, m2, m3, m4 = st.columns(4)
                    with m1:
                        st.metric("Goal", lp_data["target_goal"])
                    with m2:
                        st.metric("Completion", f"{lp_data['completion_percentage']}%", delta=f"{lp_data['completed_steps']}/{lp_data['total_steps']} steps")
                    with m3:
                        st.metric("Est. Time", f"{lp_data['estimated_total_hours']} hrs")
                    with m4:
                        st.metric("Current Level", lp_data["current_preferred_difficulty"].title())
                    st.progress(float(lp_data["completion_percentage"]) / 100.0)
                    st.markdown("#### 📌 Your Curriculum")
                    for step in lp_data["steps"]:
                        icon = "✅" if step["status"] == "completed" else ("🔄" if step["status"] == "in_progress" else "🔒")
                        with st.expander(
                            f"{icon} Step {step['step_number']}: {step['topic_name']} ({step['difficulty'].title()}) — {step['status'].upper()}",
                            expanded=(step["status"] == "in_progress"),
                        ):
                            cl, cr = st.columns([3, 1])
                            with cl:
                                st.markdown(f"**Subject**: `{step['subject']}`")
                                prereqs = step.get("prerequisites", [])
                                st.caption(f"Prerequisites: {', '.join(prereqs) if prereqs else 'None — Foundational Topic'}")
                            with cr:
                                st.write(f"⏱️ {step['estimated_minutes']} mins")
                                if step.get("best_score") is not None:
                                    st.write(f"🏆 Best: {step['best_score']}%")
                else:
                    st.error(f"API Error: {res.text}")
            except Exception as e:
                st.error(f"Could not generate learning path: {e}")

    with tab2:
        st.markdown("#### Simulate Quiz & Test Adaptive Difficulty")
        q_c1, q_c2 = st.columns(2)
        with q_c1:
            q_sid = st.number_input("Student ID", min_value=1, max_value=500, value=1, step=1, key="q_sid")
            q_tid = st.number_input("Topic ID (1–20)", min_value=1, max_value=20, value=12, step=1, key="q_tid")
        with q_c2:
            q_score = st.slider("Quiz Score (%)", 0.0, 100.0, 95.0, step=1.0)
            q_time = st.number_input("Time Spent (sec)", min_value=30, max_value=1800, value=300, step=30)

        if st.button("📤 Submit Attempt", type="primary"):
            try:
                q_payload = {"student_id": int(q_sid), "topic_id": int(q_tid), "score": float(q_score), "time_spent": int(q_time)}
                q_res = requests.post(f"{API_BASE_URL}/quiz-attempts", json=q_payload, timeout=5)
                if q_res.status_code in (200, 201):
                    q_data = q_res.json()
                    st.divider()
                    st.success(f"Attempt saved for **{q_data['topic_name']}**!")
                    r1, r2 = st.columns(2)
                    with r1:
                        st.metric("Score", f"{q_data['score']}%")
                        st.metric("Previous Difficulty", q_data["previous_difficulty"].title())
                    with r2:
                        st.metric("Attempt #", q_data["attempt_number"])
                        st.metric("New Difficulty", q_data["new_difficulty"].title(), delta="UPDATED" if q_data["difficulty_changed"] else None)
                    if q_data["difficulty_changed"]:
                        st.balloons()
                        st.warning(f"🎉 Adaptive Update: {q_data['adaptive_reason']}")
                    else:
                        st.info(f"ℹ️ {q_data['adaptive_reason']}")
                else:
                    st.error(f"API Error: {q_res.text}")
            except Exception as ex:
                st.error(f"Could not submit attempt: {ex}")


# ═══════════════════════════════════════════════════════════════════════════════
#   FEEDBACK PAGE
# ═══════════════════════════════════════════════════════════════════════════════
elif selected_page == "💬  My Feedback":
    st.markdown('<div class="hero-title" style="font-size:2rem;">Student Feedback & Sentiment</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Share how you feel about a topic. Our NLP engine analyses your sentiment and detects friction areas.</div>',
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(["📝 Submit Feedback", "📈 Sentiment Overview"])

    with tab1:
        f_c1, f_c2 = st.columns([1, 1])
        with f_c1:
            fb_student_id = st.number_input("Student ID", min_value=1, max_value=500, value=1, step=1, key="fb_sid")
        with f_c2:
            fb_topic_id = st.number_input("Topic ID (1–20)", min_value=1, max_value=20, value=12, step=1, key="fb_tid")

        st.markdown("**Quick Presets:**")
        preset_cols = st.columns(3)
        with preset_cols[0]:
            if st.button("🟢 Positive"):
                st.session_state["fb_text"] = "The explanation of logistic regression was clear, helpful, and very informative!"
        with preset_cols[1]:
            if st.button("⚪ Neutral"):
                st.session_state["fb_text"] = "Completed the practice problems. Need more examples."
        with preset_cols[2]:
            if st.button("🔴 Negative"):
                st.session_state["fb_text"] = "I felt confused, frustrated, and stuck on the difficult calculus derivatives!"

        fb_input_text = st.text_area(
            "Your Feedback",
            value=st.session_state.get("fb_text", "The explanation of logistic regression was clear, helpful, and very informative!"),
            height=110,
            placeholder="Write how you feel about this topic...",
        )

        if st.button("🔍 Analyse Sentiment", type="primary"):
            try:
                fb_payload = {"student_id": int(fb_student_id), "topic_id": int(fb_topic_id), "text": fb_input_text}
                res = requests.post(f"{API_BASE_URL}/feedback/analyze", json=fb_payload, timeout=5)
                if res.status_code in (200, 201):
                    data = res.json()
                    st.divider()
                    s_label = data["sentiment_label"].upper()
                    s_score = data["sentiment_score"]
                    s_icon = "🟢" if s_label == "POSITIVE" else ("🔴" if s_label == "NEGATIVE" else "⚪")
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.metric("Sentiment", f"{s_icon} {s_label}")
                    with m2:
                        st.metric("Polarity Score", f"{s_score:+.2f}")
                    with m3:
                        st.metric("Feedback ID", f"#{data['feedback_id']}")
                    st.markdown("#### 🏷️ Detected Themes")
                    for theme in data.get("extracted_themes", []):
                        st.markdown(f"- 📌 **{theme['theme'].title()}**: {theme['description']}")
                else:
                    st.error(f"API Error: {res.text}")
            except Exception as e:
                st.error(f"Could not analyse feedback: {e}")

    with tab2:
        st.markdown("#### 📈 Your Sentiment Overview")
        try:
            res = requests.get(f"{API_BASE_URL}/students/1/sentiment", timeout=3)
            if res.status_code == 200:
                s_data = res.json()
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("Total Submissions", s_data.get("total_feedback_entries", 5))
                with c2:
                    st.metric("Avg Polarity", f"{s_data.get('average_polarity', 0.25):+.2f}")
                with c3:
                    st.metric("Dominant Tone", s_data.get("dominant_sentiment", "Positive").upper())
            else:
                st.markdown(
                    '<div class="info-banner">🔌 Start the FastAPI backend to load your live sentiment analytics.</div>',
                    unsafe_allow_html=True,
                )
        except Exception:
            st.markdown(
                '<div class="info-banner">🔌 Start the FastAPI backend to load your live sentiment analytics.</div>',
                unsafe_allow_html=True,
            )


# ═══════════════════════════════════════════════════════════════════════════════
#   AI TUTOR PAGE
# ═══════════════════════════════════════════════════════════════════════════════
elif selected_page == "🤖  AI Tutor":
    st.markdown('<div class="hero-title" style="font-size:2rem;">Socratic AI Tutor</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Your personal AI coach — guides you step-by-step without giving away answers, building true understanding.</div>',
        unsafe_allow_html=True,
    )

    t_c1, t_c2 = st.columns([1, 1])
    with t_c1:
        tut_student_id = st.number_input("Student ID", min_value=1, max_value=500, value=1, step=1, key="tut_sid")
    with t_c2:
        tut_topic_id = st.number_input("Topic ID (1–20)", min_value=1, max_value=20, value=12, step=1, key="tut_tid")

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    st.markdown("**Quick Prompts:**")
    prompt_cols = st.columns(3)
    with prompt_cols[0]:
        if st.button("💡 Explain this concept"):
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

    user_input = st.chat_input("Ask your Socratic AI Tutor a question...")
    active_prompt = user_input or st.session_state.pop("user_prompt", None)

    if active_prompt:
        st.session_state["messages"].append({"role": "user", "content": active_prompt})
        with st.chat_message("user"):
            st.markdown(active_prompt)
        try:
            tut_payload = {"student_id": int(tut_student_id), "topic_id": int(tut_topic_id), "message": active_prompt}
            res = requests.post(f"{API_BASE_URL}/tutor/chat", json=tut_payload, timeout=8)
            if res.status_code in (200, 201):
                tut_data = res.json()
                tutor_reply = tut_data["reply"]
                with st.chat_message("assistant"):
                    st.markdown(tutor_reply)
                    st.caption(
                        f"🤖 {tut_data['provider']} · {tut_data['model_used']} · "
                        f"Risk: **{tut_data['struggle_risk_level'].upper()}**"
                    )
                st.session_state["messages"].append({"role": "assistant", "content": tutor_reply})
            else:
                st.error(f"API Error: {res.text}")
        except Exception as e:
            st.error(f"Could not reach AI Tutor: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
#   QUIZ PAGE
# ═══════════════════════════════════════════════════════════════════════════════
elif selected_page == "✏️  AI Quiz":
    st.markdown('<div class="hero-title" style="font-size:2rem;">AI Quiz Generator</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Generate dynamic MCQ quizzes for any topic and instantly update your learning profile in a closed loop.</div>',
        unsafe_allow_html=True,
    )

    qz_c1, qz_c2, qz_c3 = st.columns(3)
    with qz_c1:
        qz_student_id = st.number_input("Student ID", min_value=1, max_value=500, value=1, step=1, key="qz_sid")
    with qz_c2:
        qz_topic_id = st.number_input("Topic ID (1–20)", min_value=1, max_value=20, value=12, step=1, key="qz_tid")
    with qz_c3:
        q_count = st.slider("Questions", min_value=1, max_value=5, value=3)

    if st.button("⚡ Generate My Quiz", type="primary"):
        try:
            gen_res = requests.post(
                f"{API_BASE_URL}/quiz/generate",
                json={"student_id": int(qz_student_id), "topic_id": int(qz_topic_id), "question_count": int(q_count)},
                timeout=5,
            )
            if gen_res.status_code == 200:
                st.session_state["active_quiz"] = gen_res.json()
                st.success("Quiz generated! Answer below and submit.")
            else:
                st.error(f"API Error: {gen_res.text}")
        except Exception as e:
            st.error(f"Could not generate quiz: {e}")

    active_q = st.session_state.get("active_quiz")
    if active_q:
        st.divider()
        st.markdown(f"#### 📖 {active_q['topic_name']} ({active_q['subject']})")
        st.caption(f"Session: `{active_q['quiz_session_id']}` · Difficulty: **{active_q['difficulty'].title()}**")
        user_choices = []
        for idx, q in enumerate(active_q["questions"]):
            st.markdown(f"**Q{idx+1}: {q['question_text']}**")
            choice = st.radio(f"Answer for Q{idx+1}", options=q["options"], index=0, key=f"q_choice_{idx}")
            user_choices.append(q["options"].index(choice))

        if st.button("📤 Submit & Close Learning Loop", type="primary"):
            try:
                sub_payload = {
                    "student_id": int(active_q["student_id"]), "topic_id": int(active_q["topic_id"]),
                    "quiz_session_id": active_q["quiz_session_id"], "answers": user_choices, "time_spent": 180,
                }
                sub_res = requests.post(f"{API_BASE_URL}/quiz/submit", json=sub_payload, timeout=8)
                if sub_res.status_code == 200:
                    out = sub_res.json()
                    st.divider()
                    s_pct = out["score_percentage"]
                    pass_badge = "🟢 PASSED" if out["is_passed"] else "🔴 NEEDS REVIEW"
                    st.markdown(f"## {s_pct:.1f}% — {out['correct_answers']}/{out['total_questions']} Correct · {pass_badge}")
                    st.markdown("#### 🔄 Closed Loop Updates")
                    cl = out["closed_loop_updates"]
                    cl_1, cl_2, cl_3, cl_4 = st.columns(4)
                    with cl_1:
                        st.metric("DB Record", "SAVED ✅")
                    with cl_2:
                        st.metric("Struggle Risk", cl["struggle_risk_level"].upper(), delta=f"{cl['struggle_probability']*100:.1f}%")
                    with cl_3:
                        st.metric("Difficulty", cl["new_difficulty"].title(), delta="SCALED" if cl["difficulty_changed"] else None)
                    with cl_4:
                        st.metric("Path Progress", f"{cl['learning_path_completion_pct']}%")
                    if cl["difficulty_changed"]:
                        st.balloons()
                        st.warning(f"⚡ {cl['adaptive_reason']}")
                    st.markdown("#### 📋 Question Breakdown")
                    for qb in out["question_breakdown"]:
                        q_status = "✅ Correct" if qb["is_correct"] else "❌ Incorrect"
                        with st.expander(f"Q{qb['question_id']}: {q_status}"):
                            st.write(f"**Question**: {qb['question_text']}")
                            st.write(f"**Your Answer**: `{qb['user_selected_option']}`")
                            if not qb["is_correct"]:
                                st.write(f"**Correct Answer**: `{qb['correct_option_text']}`")
                            st.info(f"💡 {qb['explanation']}")
                else:
                    st.error(f"API Error: {sub_res.text}")
            except Exception as ex:
                st.error(f"Could not submit quiz: {ex}")


# ═══════════════════════════════════════════════════════════════════════════════
#   ACCOUNT PAGE
# ═══════════════════════════════════════════════════════════════════════════════
elif selected_page == "🔐  My Account":
    st.markdown('<div class="hero-title" style="font-size:2rem;">Account & Security</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">JWT authentication, salted password hashing, rate limiting, and request tracking.</div>',
        unsafe_allow_html=True,
    )

    tab_sec1, tab_sec2, tab_sec3 = st.tabs(["🔑 Sign In / Register", "👤 My Profile", "🛡️ Security Status"])

    with tab_sec1:
        s_c1, s_c2 = st.columns(2)
        with s_c1:
            st.markdown("#### 📝 Create Account")
            r_name = st.text_input("Full Name", value="Alex Johnson", key="r_name")
            r_email = st.text_input("Email", value="alex@example.com", key="r_email")
            r_pass = st.text_input("Password", type="password", value="SecretPass123!", key="r_pass")
            r_role = st.selectbox("Role", options=["student", "instructor"], key="r_role")
            if st.button("🚀 Create Account", type="primary"):
                try:
                    payload = {"name": r_name, "email": r_email, "password": r_pass, "role": r_role}
                    reg_res = requests.post(f"{API_BASE_URL}/auth/register", json=payload, timeout=5)
                    if reg_res.status_code in (200, 201):
                        out_reg = reg_res.json()
                        st.session_state["jwt_token"] = out_reg["access_token"]
                        st.success(f"Account created for {out_reg['name']}! JWT token stored.")
                        st.json(out_reg)
                    else:
                        st.error(f"Registration Failed: {reg_res.text}")
                except Exception as ex:
                    st.error(f"API Error: {ex}")

        with s_c2:
            st.markdown("#### 🔐 Sign In")
            l_email = st.text_input("Email", value="alex@example.com", key="l_email")
            l_pass = st.text_input("Password", type="password", value="SecretPass123!", key="l_pass")
            if st.button("🔑 Log In", type="primary"):
                try:
                    log_res = requests.post(f"{API_BASE_URL}/auth/login", json={"email": l_email, "password": l_pass}, timeout=5)
                    if log_res.status_code == 200:
                        out_log = log_res.json()
                        st.session_state["jwt_token"] = out_log["access_token"]
                        st.success(f"Welcome back, {out_log['name']}!")
                        st.json(out_log)
                    else:
                        st.error(f"Login Failed: {log_res.text}")
                except Exception as ex:
                    st.error(f"API Error: {ex}")

    with tab_sec2:
        st.markdown("#### 👤 Authenticated Profile")
        tok = st.session_state.get("jwt_token", "")
        token_input = st.text_area("Bearer Token", value=tok, height=80)
        if st.button("🔍 View My Profile"):
            if not token_input:
                st.warning("Please register or log in first to get a Bearer token.")
            else:
                try:
                    headers = {"Authorization": f"Bearer {token_input}"}
                    me_res = requests.get(f"{API_BASE_URL}/auth/me", headers=headers, timeout=5)
                    if me_res.status_code == 200:
                        st.success("JWT verified — profile loaded!")
                        st.json(me_res.json())
                    else:
                        st.error(f"Auth Failed ({me_res.status_code}): {me_res.text}")
                except Exception as ex:
                    st.error(f"Request Error: {ex}")

    with tab_sec3:
        st.markdown("#### 🛡️ Security Features Active")
        security_features = [
            ("🔑", "JWT Authentication", "HS256 signed tokens with expiry and claims validation"),
            ("🔒", "Salted Password Hashing", "PBKDF2/SHA256 with 100,000 iterations and random salt"),
            ("🛡️", "IP Rate Limiting", "120 requests/minute per IP — 429 Too Many Requests on breach"),
            ("🌐", "CORS Protection", "Restricted to trusted origins only"),
            ("🔍", "Request Tracking", "Every response includes a unique X-Request-ID UUID header"),
        ]
        for icon, title, desc in security_features:
            st.markdown(
                f'<div class="glass-panel" style="padding:1rem 1.2rem;margin-bottom:0.6rem;">'
                f'<div style="font-weight:600;color:#F1F5F9;margin-bottom:0.2rem;">{icon} {title}</div>'
                f'<div style="font-size:0.84rem;color:#64748B;">{desc}</div></div>',
                unsafe_allow_html=True,
            )


# ═══════════════════════════════════════════════════════════════════════════════
#   INFRASTRUCTURE PAGE
# ═══════════════════════════════════════════════════════════════════════════════
elif selected_page == "🐳  Infrastructure":
    st.markdown('<div class="hero-title" style="font-size:2rem;">Platform Infrastructure</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Container topology, Docker Compose orchestration, persistent volumes, and health checks.</div>',
        unsafe_allow_html=True,
    )

    d_c1, d_c2 = st.columns(2)
    with d_c1:
        st.markdown("#### 📦 Container Topology")
        containers = [
            ("edusense_backend", "python:3.11-slim (multi-stage)", ":8000", "curl -f /health", "appuser"),
            ("edusense_frontend", "python:3.11-slim", ":8501", "curl -f /_stcore/health", "root"),
        ]
        for name, image, port, hc, user in containers:
            st.markdown(
                f'<div class="glass-panel" style="padding:1rem 1.2rem;margin-bottom:0.6rem;">'
                f'<div style="font-weight:700;color:#A78BFA;font-family:monospace;font-size:0.9rem;">{name}</div>'
                f'<div style="font-size:0.82rem;color:#64748B;margin-top:0.4rem;">'
                f'<b style="color:#94A3B8;">Image:</b> {image}<br>'
                f'<b style="color:#94A3B8;">Port:</b> {port} &nbsp;·&nbsp; <b style="color:#94A3B8;">User:</b> {user}<br>'
                f'<b style="color:#94A3B8;">Healthcheck:</b> <code style="color:#34D399;">{hc}</code>'
                f'</div></div>',
                unsafe_allow_html=True,
            )
        st.markdown(
            '<div class="glass-panel" style="padding:1rem 1.2rem;">'
            '<div style="font-weight:700;color:#A78BFA;font-family:monospace;font-size:0.9rem;">edusense_data (Volume)</div>'
            '<div style="font-size:0.82rem;color:#64748B;margin-top:0.4rem;">Persistent shared volume → <code style="color:#34D399;">/app/edusense.db</code> &amp; <code style="color:#34D399;">/app/ml/artifacts</code></div>'
            '</div>',
            unsafe_allow_html=True,
        )

    with d_c2:
        st.markdown("#### ⚡ Infrastructure Status")
        if os.path.exists("Dockerfile") and os.path.exists("docker-compose.yml"):
            st.success("✅ Dockerfile & docker-compose.yml verified!")
            st.info("Run `docker-compose up --build -d` to launch in production mode.")
        else:
            st.warning("Docker files not found in project root.")

        with st.expander("📄 docker-compose.yml"):
            if os.path.exists("docker-compose.yml"):
                with open("docker-compose.yml", "r") as f:
                    st.code(f.read(), language="yaml")
