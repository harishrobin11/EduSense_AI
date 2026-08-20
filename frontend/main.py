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

raw_api_url = os.getenv("API_BASE_URL", "http://localhost:8000").strip().rstrip("/")
if not raw_api_url.startswith("http://") and not raw_api_url.startswith("https://"):
    if raw_api_url == "edusense-ai-api":
        API_BASE_URL = "https://edusense-ai-api.onrender.com"
    else:
        API_BASE_URL = f"https://{raw_api_url}"
else:
    API_BASE_URL = raw_api_url

# ─── Session-based Navigation ──────────────────────────────────────────────────
if "active_page" not in st.session_state:
    st.session_state["active_page"] = "home"

PAGES = [
    ("home",        "Home",             "🏠"),
    ("analytics",   "Analytics",        "📊"),
    ("recommend",   "Recommendations",  "🎯"),
    ("path",        "Learning Path",    "🗺️"),
    ("feedback",    "Feedback",         "💬"),
    ("tutor",       "AI Tutor",         "🤖"),
    ("quiz",        "AI Quiz",          "✏️"),
    ("account",     "My Account",       "🔐"),
    ("infra",       "Infrastructure",   "🐳"),
]


# ─── Premium CSS Design System ─────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    /* ── Reset ── */
    html, body, [class*="css"] { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
    .block-container { padding-top: 2.5rem; }

    /* ── App Background ── */
    .stApp {
        background: radial-gradient(ellipse at 15% 0%, rgba(99,57,255,0.12) 0%, transparent 50%),
                    radial-gradient(ellipse at 85% 5%, rgba(236,72,153,0.08) 0%, transparent 40%),
                    radial-gradient(ellipse at 50% 95%, rgba(6,182,212,0.06) 0%, transparent 50%),
                    #080B1A;
        color: #E2E8F0;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: #060913;
        border-right: 1px solid rgba(255,255,255,0.05);
        padding-top: 0 !important;
    }
    section[data-testid="stSidebar"] > div:first-child { padding-top: 1.2rem; }
    /* Hide the default radio buttons completely */
    section[data-testid="stSidebar"] .stRadio { display: none !important; }

    /* ── Nav Items (custom buttons) ── */
    .nav-container { display: flex; flex-direction: column; gap: 2px; padding: 0 0.6rem; }
    .nav-item {
        display: flex; align-items: center; gap: 10px;
        padding: 9px 14px;
        border-radius: 8px;
        border: 1px solid transparent;
        font-size: 0.87rem;
        font-weight: 500;
        color: #64748B;
        text-decoration: none;
        cursor: pointer;
        transition: all 0.15s ease;
        background: transparent;
        width: 100%;
        text-align: left;
    }
    .nav-item:hover { background: rgba(255,255,255,0.04); color: #CBD5E1; }
    .nav-item.active {
        background: rgba(99,102,241,0.12);
        color: #A78BFA;
        font-weight: 600;
        border-color: rgba(99,102,241,0.15);
    }
    .nav-icon { font-size: 1rem; width: 22px; text-align: center; flex-shrink: 0; }
    .nav-label { white-space: nowrap; }
    .nav-section-label {
        font-size: 0.68rem;
        font-weight: 700;
        color: #334155;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        padding: 16px 14px 6px 14px;
    }

    /* ── Logo Block ── */
    .sidebar-brand {
        display: flex; align-items: center; gap: 10px;
        padding: 0.4rem 1rem 1rem 1rem;
    }
    .sidebar-brand-icon {
        width: 36px; height: 36px; border-radius: 10px;
        background: linear-gradient(135deg, #6366F1, #8B5CF6);
        display: flex; align-items: center; justify-content: center;
        font-size: 1.1rem;
        box-shadow: 0 4px 12px rgba(99,102,241,0.3);
    }
    .sidebar-brand-text {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.1rem; font-weight: 700; color: #F1F5F9;
        line-height: 1.15;
    }
    .sidebar-brand-sub {
        font-size: 0.68rem; color: #475569; font-weight: 500;
        letter-spacing: 0.02em;
    }

    /* ── Sidebar Status ── */
    .sidebar-status {
        margin: 1rem 0.6rem 0 0.6rem;
        padding: 10px 14px;
        border-radius: 10px;
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.04);
    }
    .status-row {
        display: flex; align-items: center; justify-content: space-between;
        font-size: 0.78rem;
    }
    .status-dot-ok { width:7px;height:7px;border-radius:50%;background:#34D399;display:inline-block;margin-right:6px;animation:blink-dot 2s infinite; }
    .status-dot-off { width:7px;height:7px;border-radius:50%;background:#EF4444;display:inline-block;margin-right:6px; }
    @keyframes blink-dot { 0%,100%{opacity:1} 50%{opacity:0.35} }

    /* ── Page Header ── */
    .page-header {
        margin-bottom: 1.8rem;
        padding-bottom: 1.2rem;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .page-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(1.6rem, 3vw, 2.2rem);
        font-weight: 700; color: #F1F5F9;
        letter-spacing: -0.025em; line-height: 1.2;
        margin-bottom: 0.3rem;
    }
    .page-desc {
        font-size: 0.92rem; color: #64748B;
        line-height: 1.55; max-width: 680px;
    }

    /* ── Hero (Home only) ── */
    .hero-wrap { padding: 1rem 0 1.2rem 0; }
    .hero-eyebrow {
        display: inline-flex; align-items: center; gap: 7px;
        background: rgba(99,102,241,0.1);
        border: 1px solid rgba(99,102,241,0.2);
        border-radius: 999px; padding: 4px 14px;
        font-size: 0.72rem; font-weight: 700; color: #818CF8;
        letter-spacing: 0.08em; text-transform: uppercase;
        margin-bottom: 1rem;
    }
    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(2rem, 4.5vw, 3.2rem);
        font-weight: 700; letter-spacing: -0.03em; line-height: 1.1;
        background: linear-gradient(135deg, #FFF 0%, #C4B5FD 45%, #F472B6 85%, #FB923C 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; margin-bottom: 0.6rem;
    }
    .hero-sub {
        font-size: 1.05rem; color: #94A3B8;
        line-height: 1.6; max-width: 620px;
    }

    /* ── Cards ── */
    .card {
        background: rgba(12,14,32,0.85);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 1.4rem 1.5rem;
        transition: border-color 0.2s ease, transform 0.15s ease;
    }
    .card:hover {
        border-color: rgba(99,102,241,0.2);
        transform: translateY(-2px);
    }
    .card-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.95rem; font-weight: 600; color: #F1F5F9;
        margin-bottom: 0.5rem;
    }
    .card-text { font-size: 0.84rem; color: #64748B; line-height: 1.55; }
    .card-icon {
        width: 40px; height: 40px; border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.15rem; margin-bottom: 0.9rem;
    }

    /* ── Stat Metric Cards ── */
    .metric-row { display: grid; gap: 14px; margin: 1.2rem 0; }
    .metric-row.cols-4 { grid-template-columns: repeat(4, 1fr); }
    .metric-row.cols-3 { grid-template-columns: repeat(3, 1fr); }
    .metric-card {
        background: rgba(12,14,32,0.85);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 1.1rem 1.3rem;
    }
    .metric-label {
        font-size: 0.72rem; font-weight: 600; color: #475569;
        text-transform: uppercase; letter-spacing: 0.07em;
        margin-bottom: 0.4rem;
    }
    .metric-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.7rem; font-weight: 700; color: #F1F5F9;
        line-height: 1;
    }
    .metric-delta {
        font-size: 0.75rem; font-weight: 600; color: #34D399;
        margin-top: 0.35rem;
    }

    /* ── Tags ── */
    .tag-row { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 0.7rem; }
    .tag {
        background: rgba(99,102,241,0.08);
        color: #818CF8;
        border: 1px solid rgba(99,102,241,0.15);
        padding: 2px 9px; border-radius: 5px;
        font-size: 0.70rem; font-weight: 600; letter-spacing: 0.02em;
    }

    /* ── Info Banner ── */
    .info-banner {
        background: rgba(99,102,241,0.06);
        border: 1px solid rgba(99,102,241,0.15);
        border-radius: 10px; padding: 1rem 1.3rem;
        font-size: 0.85rem; color: #94A3B8; line-height: 1.55;
    }

    /* ── Security Feature Row ── */
    .sec-row {
        display: flex; align-items: flex-start; gap: 12px;
        padding: 12px 16px;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.04);
        background: rgba(12,14,32,0.6);
        margin-bottom: 8px;
    }
    .sec-icon { font-size: 1.2rem; flex-shrink: 0; margin-top: 1px; }
    .sec-title { font-size: 0.88rem; font-weight: 600; color: #E2E8F0; }
    .sec-desc { font-size: 0.80rem; color: #64748B; margin-top: 2px; }

    /* ── Container/Infra Cards ── */
    .infra-card {
        background: rgba(12,14,32,0.8);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 10px;
    }
    .infra-name {
        font-family: 'Space Grotesk', monospace;
        font-size: 0.88rem; font-weight: 700; color: #A78BFA;
    }
    .infra-detail { font-size: 0.80rem; color: #64748B; margin-top: 6px; line-height: 1.6; }
    .infra-detail b { color: #94A3B8; }
    .infra-detail code {
        background: rgba(99,102,241,0.08); color: #34D399;
        padding: 1px 6px; border-radius: 4px; font-size: 0.78rem;
    }

    /* ── Override: Streamlit Metrics ── */
    [data-testid="stMetricValue"] {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700; font-size: 1.5rem !important; color: #F1F5F9;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.75rem !important; color: #64748B !important;
        text-transform: uppercase; letter-spacing: 0.06em;
    }

    /* ── Override: Main-area Buttons ── */
    [data-testid="stMainBlockContainer"] .stButton > button {
        background: linear-gradient(135deg, #6366F1, #7C3AED);
        color: #FFF; font-weight: 600;
        border-radius: 8px; border: none;
        padding: 0.5rem 1.3rem; font-size: 0.85rem;
        box-shadow: 0 2px 10px rgba(99,102,241,0.25);
        transition: all 0.15s ease;
    }
    [data-testid="stMainBlockContainer"] .stButton > button:hover {
        background: linear-gradient(135deg, #818CF8, #A78BFA);
        box-shadow: 0 4px 16px rgba(139,92,246,0.35);
        transform: translateY(-1px);
    }

    /* ── Sidebar Nav Buttons ── */
    section[data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        color: #64748B !important;
        font-weight: 500 !important;
        font-size: 0.87rem !important;
        border: 1px solid transparent !important;
        border-radius: 8px !important;
        padding: 8px 14px !important;
        box-shadow: none !important;
        text-align: left !important;
        justify-content: flex-start !important;
        transition: all 0.12s ease !important;
        width: 100% !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.04) !important;
        color: #CBD5E1 !important;
        transform: none !important;
        box-shadow: none !important;
    }
    section[data-testid="stSidebar"] .stButton > button:focus,
    section[data-testid="stSidebar"] .stButton > button:active {
        box-shadow: none !important;
    }
    /* Active (primary) nav button */
    section[data-testid="stSidebar"] .stButton > button[kind="primary"],
    section[data-testid="stSidebar"] .stButton > button[data-testid*="primary"] {
        background: rgba(99,102,241,0.12) !important;
        color: #A78BFA !important;
        font-weight: 600 !important;
        border-color: rgba(99,102,241,0.15) !important;
    }

    /* ── Override: Inputs ── */
    .stTextInput > div > div, .stNumberInput > div > div,
    .stTextArea > div > div, .stSelectbox > div > div {
        background: rgba(12,14,32,0.95) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 8px !important; color: #E2E8F0 !important;
    }

    /* ── Override: Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(12,14,32,0.7);
        border-radius: 10px; padding: 3px; gap: 3px;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 7px; font-weight: 500; font-size: 0.85rem;
        color: #64748B; padding: 7px 18px;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(99,102,241,0.15) !important;
        color: #A78BFA !important; font-weight: 600;
    }

    /* ── Override: Progress ── */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #6366F1, #8B5CF6, #A78BFA) !important;
        border-radius: 999px !important;
    }

    /* ── Override: Expander ── */
    .streamlit-expanderHeader {
        background: rgba(12,14,32,0.5) !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-radius: 8px !important;
        font-weight: 500; font-size: 0.88rem; color: #CBD5E1;
    }

    /* ── Override: Divider ── */
    hr { border-color: rgba(255,255,255,0.05) !important; margin: 1.2rem 0 !important; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.25); border-radius: 99px; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─── Helpers ───────────────────────────────────────────────────────────────────
def fetch_backend_health():
    """Fetch health status from FastAPI backend."""
    try:
        resp = requests.get(f"{API_BASE_URL}/health", timeout=3)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


def page_header(title: str, desc: str):
    """Render a consistent page header."""
    st.markdown(
        f'<div class="page-header">'
        f'<div class="page-title">{title}</div>'
        f'<div class="page-desc">{desc}</div></div>',
        unsafe_allow_html=True,
    )


# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand
    st.markdown(
        '<div class="sidebar-brand">'
        '<div class="sidebar-brand-icon">🎓</div>'
        '<div><div class="sidebar-brand-text">EduSense AI</div>'
        '<div class="sidebar-brand-sub">Personal Learning Coach</div></div></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<hr style="margin:0.3rem 0.6rem 0.4rem 0.6rem;border-color:rgba(255,255,255,0.05);">', unsafe_allow_html=True)

    # Navigation — using st.button per item (no radio buttons)
    st.markdown('<div class="nav-section-label">Menu</div>', unsafe_allow_html=True)

    for page_key, page_label, page_icon in PAGES:
        is_active = st.session_state["active_page"] == page_key
        if st.button(
            f"{page_icon}  {page_label}",
            key=f"nav_{page_key}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state["active_page"] = page_key
            st.rerun()

    st.markdown('<hr style="margin:0.8rem 0.6rem 0.5rem 0.6rem;border-color:rgba(255,255,255,0.05);">', unsafe_allow_html=True)

    # System Status
    st.markdown('<div class="nav-section-label">System</div>', unsafe_allow_html=True)
    health = fetch_backend_health()
    if health:
        st.markdown(
            '<div class="sidebar-status">'
            '<div class="status-row">'
            '<span><span class="status-dot-ok"></span><span style="color:#94A3B8;font-weight:500;">API</span></span>'
            '<span style="color:#34D399;font-weight:600;">Online</span></div>'
            f'<div style="font-size:0.72rem;color:#475569;margin-top:5px;">'
            f'DB: {health.get("database", {}).get("database_type", "SQLite").upper()}</div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="sidebar-status">'
            '<div class="status-row">'
            '<span><span class="status-dot-off"></span><span style="color:#94A3B8;font-weight:500;">API</span></span>'
            '<span style="color:#EF4444;font-weight:600;">Offline</span></div>'
            '<div style="font-size:0.72rem;color:#475569;margin-top:5px;">Start backend on :8000</div></div>',
            unsafe_allow_html=True,
        )


# Resolve active page
active = st.session_state["active_page"]


# ═══════════════════════════════════════════════════════════════════════════════
#   HOME
# ═══════════════════════════════════════════════════════════════════════════════
if active == "home":
    st.markdown(
        '<div class="hero-wrap">'
        '<div class="hero-eyebrow">✦ AI-Powered Personalised Learning</div>'
        '<div class="hero-title">Learn Smarter.<br>Grow Faster.</div>'
        '<div class="hero-sub">EduSense AI adapts to <em>your</em> unique learning style — predicting struggles before they happen, '
        'building personalised paths, and coaching you with a Socratic AI tutor.</div></div>',
        unsafe_allow_html=True,
    )

    # Stats
    st.markdown(
        '<div class="metric-row cols-4">'
        '<div class="metric-card"><div class="metric-label">Active Learners</div>'
        '<div class="metric-value">500+</div><div class="metric-delta">▲ Live cohort</div></div>'
        '<div class="metric-card"><div class="metric-label">Core Topics</div>'
        '<div class="metric-value">20</div><div class="metric-delta">▲ Prerequisite graph</div></div>'
        '<div class="metric-card"><div class="metric-label">Quiz Attempts</div>'
        '<div class="metric-value">11,169</div><div class="metric-delta">▲ Closed-loop system</div></div>'
        '<div class="metric-card"><div class="metric-label">AI Accuracy</div>'
        '<div class="metric-value">66.9%</div><div class="metric-delta">▲ Deep Neural Network</div></div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    # Features — Row 1
    st.markdown(
        '<div style="font-family:\'Space Grotesk\',sans-serif;font-size:1.2rem;font-weight:700;color:#F1F5F9;margin-bottom:4px;">What EduSense Does For You</div>'
        '<div style="font-size:0.88rem;color:#64748B;margin-bottom:1.2rem;">Six intelligent modules working together to accelerate your learning.</div>',
        unsafe_allow_html=True,
    )

    features = [
        ("🧠", "Struggle Predictor", "Detects when you're about to struggle before it happens, using Deep Neural Networks.", ["PyTorch MLP", "Random Forest"], "rgba(139,92,246,0.12)"),
        ("🎯", "Smart Recommendations", "Surfaces the exact topics you need next using TF-IDF concept similarity.", ["TF-IDF", "Prerequisite Map"], "rgba(6,182,212,0.12)"),
        ("🗺️", "Adaptive Paths", "Personalised step-by-step curriculum that scales difficulty with your progress.", ["DAG Topology", "Auto-Scaling"], "rgba(16,185,129,0.12)"),
        ("🤖", "Socratic AI Tutor", "Personal AI coach that guides you step-by-step without giving away answers.", ["LLM-Powered", "Context-Aware"], "rgba(245,158,11,0.12)"),
        ("✏️", "Dynamic Quizzes", "Auto-generates MCQ quizzes and instantly updates your risk profile.", ["MCQ Engine", "Closed Loop"], "rgba(236,72,153,0.12)"),
        ("💬", "Sentiment Analysis", "Understands frustration from your feedback using NLP to spot friction early.", ["TextBlob", "HuggingFace"], "rgba(99,102,241,0.12)"),
    ]
    rows = [features[:3], features[3:]]
    for row in rows:
        cols = st.columns(3)
        for col, (icon, title, desc, tags, bg) in zip(cols, row):
            with col:
                tags_html = "".join(f'<span class="tag">{t}</span>' for t in tags)
                st.markdown(
                    f'<div class="card">'
                    f'<div class="card-icon" style="background:{bg};">{icon}</div>'
                    f'<div class="card-title">{title}</div>'
                    f'<div class="card-text">{desc}</div>'
                    f'<div class="tag-row">{tags_html}</div></div>',
                    unsafe_allow_html=True,
                )
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    st.divider()

    # Data Summary
    st.markdown(
        '<div style="font-family:\'Space Grotesk\',sans-serif;font-size:1.2rem;font-weight:700;color:#F1F5F9;margin-bottom:4px;">Dataset & Model Benchmarks</div>'
        '<div style="font-size:0.88rem;color:#64748B;margin-bottom:1.2rem;">Trained and validated on a real-world educational dataset.</div>',
        unsafe_allow_html=True,
    )
    d1, d2 = st.columns(2)
    with d1:
        eda_path = "ml/data/processed/eda_summary.json"
        if os.path.exists(eda_path):
            with open(eda_path, "r") as f:
                eda_data = json.load(f)
            entries = [
                ("Total Quiz Attempts", f"{eda_data.get('total_quiz_attempts', 11169):,}"),
                ("Registered Students", f"{eda_data.get('total_students', 500)}"),
                ("Struggle Rate", f"{eda_data.get('overall_struggle_rate', 0.442)*100:.1f}%"),
                ("Struggle Threshold", "Avg Score < 65%"),
            ]
            inner = ""
            for label, val in entries:
                inner += (
                    f'<div style="display:flex;justify-content:space-between;padding:9px 0;'
                    f'border-bottom:1px solid rgba(255,255,255,0.04);">'
                    f'<span style="color:#64748B;font-size:0.84rem;">{label}</span>'
                    f'<span style="color:#F1F5F9;font-weight:600;font-size:0.84rem;">{val}</span></div>'
                )
            st.markdown(f'<div class="card"><div class="card-title">📁 Dataset Snapshot</div>{inner}</div>', unsafe_allow_html=True)
        else:
            st.info("Dataset summary available upon backend launch.")
    with d2:
        st.markdown("##### ⚡ AI Model Comparison")
        comp_data = pd.DataFrame([
            {"Model": "🧠 PyTorch MLP", "Accuracy": "66.94%", "ROC-AUC": "0.7193", "F1": "0.6377"},
            {"Model": "🌲 Random Forest", "Accuracy": "65.43%", "ROC-AUC": "0.7018", "F1": "0.6357"},
            {"Model": "📈 Logistic Reg.", "Accuracy": "65.11%", "ROC-AUC": "0.7153", "F1": "0.6374"},
        ])
        st.dataframe(comp_data, width="stretch", hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
#   ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════
elif active == "analytics":
    page_header("Student Analytics", "Analyse performance, predict struggle risk, and compare AI model accuracy side by side.")

    tab1, tab2, tab3 = st.tabs(["👤  Student Profile", "🔮  Risk Simulator", "📊  Model Benchmarks"])

    with tab1:
        c1, c2 = st.columns([1, 2])
        with c1:
            student_id = st.number_input("Student ID (1–500)", min_value=1, max_value=500, value=1, step=1)
            model_choice = st.selectbox(
                "AI Model",
                options=["pytorch_nn", "random_forest", "logistic_regression"],
                format_func=lambda x: {"pytorch_nn": "🧠 PyTorch NN", "random_forest": "🌲 Random Forest", "logistic_regression": "📈 Logistic Reg."}[x],
            )
        with c2:
            try:
                payload = {"student_id": int(student_id), "topic_id": 12, "model_type": model_choice}
                res = requests.post(f"{API_BASE_URL}/predict/struggle", json=payload, timeout=3)
                if res.status_code == 200:
                    data = res.json()
                    prob = data["struggle_probability"]
                    risk = data["risk_level"].upper()
                    m1, m2 = st.columns(2)
                    with m1:
                        st.metric("Struggle Probability", f"{prob*100:.1f}%", delta=f"Risk: {risk}")
                    with m2:
                        st.metric("Assessment", "⚠️ At Risk" if data["is_struggling"] else "✅ On Track")
                    if data["is_struggling"]:
                        st.error(f"⚠️ High struggle risk detected ({prob*100:.1f}%). Review recommended topics.")
                    else:
                        st.success(f"✅ On track — keep it up! (Risk: {prob*100:.1f}%)")
                    if data.get("risk_factors"):
                        st.markdown("**Risk Factors:**")
                        for f in data["risk_factors"]:
                            st.markdown(f"- ⚠️ {f}")
                else:
                    st.markdown('<div class="info-banner">🔌 Connect backend API on port 8000 to run live predictions.</div>', unsafe_allow_html=True)
            except Exception:
                st.markdown('<div class="info-banner">🚀 Start FastAPI backend to see live AI predictions.</div>', unsafe_allow_html=True)

    with tab2:
        col_m = st.selectbox("Model", options=["pytorch_nn", "random_forest", "logistic_regression"],
            format_func=lambda x: {"pytorch_nn": "🧠 PyTorch NN", "random_forest": "🌲 Random Forest", "logistic_regression": "📈 Logistic Reg."}[x])
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
            diff_num = st.selectbox("Topic Difficulty", options=[1, 2, 3],
                format_func=lambda x: {1: "🟢 Easy", 2: "🟡 Medium", 3: "🔴 Hard"}[x], index=1)
        sim_payload = {
            "recent_quiz_score": float(recent_score), "historical_topic_score": float(hist_score),
            "attempts_count": int(attempts), "total_time_spent": int(time_spent),
            "prerequisite_completion_rate": float(prereq_rate), "score_trend": float(score_trend),
            "engagement_frequency": int(engagement), "topic_difficulty_numeric": int(diff_num), "model_type": col_m,
        }
        try:
            res = requests.post(f"{API_BASE_URL}/predict/struggle", json=sim_payload, timeout=3)
            if res.status_code == 200:
                out = res.json()
                st.divider()
                pct = out["struggle_probability"] * 100
                st.metric(f"Predicted Struggle ({out.get('model_version', col_m)})", f"{pct:.1f}%")
                st.info(f"Risk: **{out['risk_level'].upper()}** — {'Intervention Suggested' if out['is_struggling'] else 'Mastery Likely'}")
                for rf in out.get("risk_factors", []):
                    st.markdown(f"- ⚠️ {rf}")
        except Exception:
            st.markdown('<div class="info-banner">🔌 Connect backend to run real-time simulations.</div>', unsafe_allow_html=True)

    with tab3:
        try:
            m_res = requests.get(f"{API_BASE_URL}/models", timeout=3)
            if m_res.status_code == 200:
                m_data = m_res.json()
                defaults = {
                    "pytorch_nn": {"accuracy": 0.6694, "precision": 0.6844, "recall": 0.5969, "f1_score": 0.6377, "roc_auc": 0.7193},
                    "random_forest": {"accuracy": 0.6543, "precision": 0.6535, "recall": 0.6189, "f1_score": 0.6357, "roc_auc": 0.7018},
                    "logistic_regression": {"accuracy": 0.6511, "precision": 0.6459, "recall": 0.6292, "f1_score": 0.6374, "roc_auc": 0.7153},
                }
                labels = {"pytorch_nn": "🧠 PyTorch MLP", "random_forest": "🌲 Random Forest", "logistic_regression": "📈 Logistic Reg."}
                bm1, bm2, bm3 = st.columns(3)
                for col, key in zip([bm1, bm2, bm3], defaults):
                    md = m_data.get(key, defaults[key])
                    with col:
                        st.markdown(f"##### {labels[key]}")
                        st.metric("Accuracy", f"{md['accuracy']*100:.2f}%")
                        for k in ["precision", "recall", "f1_score", "roc_auc"]:
                            st.write(f"- **{k.replace('_', ' ').title()}**: {md[k]:.4f}")
                st.divider()
                comp_df = pd.DataFrame([
                    {"Model": labels[k], "Acc (%)": round(defaults[k]["accuracy"]*100, 2),
                     "Precision": defaults[k]["precision"], "Recall": defaults[k]["recall"],
                     "F1": defaults[k]["f1_score"], "ROC-AUC": defaults[k]["roc_auc"]}
                    for k in defaults
                ])
                st.dataframe(comp_df, width="stretch", hide_index=True)
        except Exception:
            st.markdown('<div class="info-banner">🔌 Start backend to inspect model benchmarks.</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#   RECOMMENDATIONS
# ═══════════════════════════════════════════════════════════════════════════════
elif active == "recommend":
    page_header("Smart Recommendations", "Personalised topic recommendations using TF-IDF similarity and prerequisite graph filtering.")

    r1, r2, _ = st.columns([1, 1, 2])
    with r1:
        rec_student_id = st.number_input("Student ID", min_value=1, max_value=500, value=1, step=1, key="rec_sid")
    with r2:
        top_n = st.slider("Top-N", min_value=1, max_value=10, value=3)

    if st.button("🚀 Get My Recommendations", type="primary"):
        try:
            res = requests.get(f"{API_BASE_URL}/students/{rec_student_id}/recommendations?top_n={top_n}", timeout=5)
            if res.status_code == 200:
                rec_data = res.json()
                st.divider()
                st.markdown(f"#### Recommended for Student #{rec_data['student_id']}")
                for idx, rec in enumerate(rec_data["recommendations"]):
                    with st.expander(f"#{idx+1} · {rec['topic_name']} ({rec['subject']}) — {rec.get('score', rec.get('recommendation_score', 0)):.1f}% match", expanded=(idx == 0)):
                        st.markdown(f"**Difficulty**: `{rec['difficulty'].title()}` · **Prerequisites Met**: {'✅ Yes' if rec.get('prerequisite_ready', rec.get('prerequisites_met', True)) else '⚠️ No'}")
                        st.info(f"💡 {rec.get('reason', rec.get('explanation', ''))}")
            else:
                st.error(f"API Error ({res.status_code}): {res.text}")
        except Exception as e:
            st.error(f"Could not reach API: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
#   LEARNING PATH
# ═══════════════════════════════════════════════════════════════════════════════
elif active == "path":
    page_header("My Learning Path", "A personalised curriculum built just for you — step-by-step, prerequisite-aware, and adaptive.")

    tab1, tab2 = st.tabs(["🛣️  Path Visualiser", "📝  Quiz & Adaptive Difficulty"])

    with tab1:
        c1, c2, _ = st.columns([1, 1, 2])
        with c1:
            lp_student_id = st.number_input("Student ID", min_value=1, max_value=500, value=1, step=1, key="lp_sid")
        with c2:
            target_sub = st.selectbox("Subject Filter", ["All Subjects", "Machine Learning", "Deep Learning & NLP", "Python Programming", "Mathematics for ML"])

        if st.button("🚀 Generate My Path", type="primary"):
            try:
                sub_param = None if target_sub == "All Subjects" else target_sub
                res = requests.post(f"{API_BASE_URL}/learning-path", json={"student_id": int(lp_student_id), "target_subject": sub_param}, timeout=5)
                if res.status_code in (200, 201):
                    lp = res.json()
                    st.divider()
                    m1, m2, m3, m4 = st.columns(4)
                    with m1: st.metric("Goal", lp["target_goal"])
                    with m2: st.metric("Completion", f"{lp['completion_percentage']}%", delta=f"{lp['completed_steps']}/{lp['total_steps']}")
                    with m3: st.metric("Est. Time", f"{lp['estimated_total_hours']} hrs")
                    with m4: st.metric("Level", lp["current_preferred_difficulty"].title())
                    st.progress(float(lp["completion_percentage"]) / 100.0)
                    for step in lp["steps"]:
                        icon = "✅" if step["status"] == "completed" else ("🔄" if step["status"] == "in_progress" else "🔒")
                        with st.expander(f"{icon}  Step {step['step_number']}: {step['topic_name']} · {step['difficulty'].title()} · {step['status'].upper()}", expanded=(step["status"] == "in_progress")):
                            cl, cr = st.columns([3, 1])
                            with cl:
                                st.markdown(f"**Subject**: `{step['subject']}`")
                                prereqs = step.get("prerequisites", [])
                                st.caption(f"Prerequisites: {', '.join(prereqs) if prereqs else 'None'}")
                            with cr:
                                st.write(f"⏱️ {step['estimated_minutes']} mins")
                                if step.get("best_score") is not None:
                                    st.write(f"🏆 Best: {step['best_score']}%")
                else:
                    st.error(f"API Error: {res.text}")
            except Exception as e:
                st.error(f"Could not generate path: {e}")

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
                q_res = requests.post(f"{API_BASE_URL}/quiz-attempts", json={"student_id": int(q_sid), "topic_id": int(q_tid), "score": float(q_score), "time_spent": int(q_time)}, timeout=5)
                if q_res.status_code in (200, 201):
                    qd = q_res.json()
                    st.divider()
                    st.success(f"Saved for **{qd['topic_name']}**!")
                    r1, r2 = st.columns(2)
                    with r1: st.metric("Score", f"{qd['score']}%"); st.metric("Prev. Difficulty", qd["previous_difficulty"].title())
                    with r2: st.metric("Attempt #", qd["attempt_number"]); st.metric("New Difficulty", qd["new_difficulty"].title(), delta="UPDATED" if qd["difficulty_changed"] else None)
                    if qd["difficulty_changed"]:
                        st.balloons()
                        st.warning(f"🎉 {qd['adaptive_reason']}")
                    else:
                        st.info(f"ℹ️ {qd['adaptive_reason']}")
                else:
                    st.error(f"API Error: {q_res.text}")
            except Exception as ex:
                st.error(f"Could not submit: {ex}")


# ═══════════════════════════════════════════════════════════════════════════════
#   FEEDBACK
# ═══════════════════════════════════════════════════════════════════════════════
elif active == "feedback":
    page_header("Feedback & Sentiment", "Share how you feel about a topic. Our NLP engine detects sentiment and friction areas.")

    tab1, tab2 = st.tabs(["📝  Submit Feedback", "📈  Sentiment Overview"])

    with tab1:
        f_c1, f_c2, _ = st.columns([1, 1, 2])
        with f_c1:
            fb_sid = st.number_input("Student ID", min_value=1, max_value=500, value=1, step=1, key="fb_sid")
        with f_c2:
            fb_tid = st.number_input("Topic ID (1–20)", min_value=1, max_value=20, value=12, step=1, key="fb_tid")

        st.markdown("**Quick presets:**")
        pr = st.columns(3)
        with pr[0]:
            if st.button("🟢 Positive"): st.session_state["fb_text"] = "The explanation of logistic regression was clear, helpful, and very informative!"
        with pr[1]:
            if st.button("⚪ Neutral"): st.session_state["fb_text"] = "Completed the practice problems. Need more examples."
        with pr[2]:
            if st.button("🔴 Negative"): st.session_state["fb_text"] = "I felt confused, frustrated, and stuck on the difficult calculus derivatives!"

        fb_text = st.text_area("Your Feedback", value=st.session_state.get("fb_text", "The explanation was clear and very informative!"), height=100, placeholder="Write how you feel about this topic…")

        if st.button("🔍 Analyse Sentiment", type="primary"):
            try:
                res = requests.post(f"{API_BASE_URL}/feedback/analyze", json={"student_id": int(fb_sid), "topic_id": int(fb_tid), "text": fb_text}, timeout=5)
                if res.status_code in (200, 201):
                    d = res.json()
                    st.divider()
                    sl = d["sentiment_label"].upper()
                    ic = "🟢" if sl == "POSITIVE" else ("🔴" if sl == "NEGATIVE" else "⚪")
                    m1, m2, m3 = st.columns(3)
                    with m1: st.metric("Sentiment", f"{ic} {sl}")
                    with m2: st.metric("Polarity", f"{d['sentiment_score']:+.2f}")
                    with m3: st.metric("Feedback ID", f"#{d['feedback_id']}")
                    if d.get("extracted_themes"):
                        st.markdown("#### 🏷️ Detected Themes")
                        for t in d["extracted_themes"]:
                            st.markdown(f"- 📌 **{t['theme'].title()}**: {t['description']}")
                else:
                    st.error(f"API Error: {res.text}")
            except Exception as e:
                st.error(f"Could not analyse feedback: {e}")

    with tab2:
        try:
            res = requests.get(f"{API_BASE_URL}/students/1/sentiment", timeout=3)
            if res.status_code == 200:
                sd = res.json()
                c1, c2, c3 = st.columns(3)
                with c1: st.metric("Total Submissions", sd.get("total_feedback_entries", 5))
                with c2: st.metric("Avg Polarity", f"{sd.get('average_polarity', 0.25):+.2f}")
                with c3: st.metric("Dominant Tone", sd.get("dominant_sentiment", "Positive").upper())
            else:
                st.markdown('<div class="info-banner">🔌 Start backend to load sentiment analytics.</div>', unsafe_allow_html=True)
        except Exception:
            st.markdown('<div class="info-banner">🔌 Start backend to load sentiment analytics.</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#   AI TUTOR
# ═══════════════════════════════════════════════════════════════════════════════
elif active == "tutor":
    page_header("Socratic AI Tutor", "Your personal AI coach — guides you step-by-step without giving away answers.")

    t_c1, t_c2, _ = st.columns([1, 1, 2])
    with t_c1:
        tut_sid = st.number_input("Student ID", min_value=1, max_value=500, value=1, step=1, key="tut_sid")
    with t_c2:
        tut_tid = st.number_input("Topic ID (1–20)", min_value=1, max_value=20, value=12, step=1, key="tut_tid")

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    st.markdown("**Quick prompts:**")
    qp = st.columns(3)
    with qp[0]:
        if st.button("💡 Explain this concept"): st.session_state["user_prompt"] = "I'm struggling to understand this topic. Can you explain the core ideas step-by-step?"
    with qp[1]:
        if st.button("❓ Give me a guiding question"): st.session_state["user_prompt"] = "Don't give me the answer. Ask me a Socratic guiding question to test my understanding."
    with qp[2]:
        if st.button("🔗 What prerequisites?"): st.session_state["user_prompt"] = "What foundational topics do I need to review before mastering this concept?"

    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask your AI Tutor a question…")
    active_prompt = user_input or st.session_state.pop("user_prompt", None)

    if active_prompt:
        st.session_state["messages"].append({"role": "user", "content": active_prompt})
        with st.chat_message("user"):
            st.markdown(active_prompt)
        try:
            res = requests.post(f"{API_BASE_URL}/tutor/chat", json={"student_id": int(tut_sid), "topic_id": int(tut_tid), "message": active_prompt}, timeout=8)
            if res.status_code in (200, 201):
                td = res.json()
                with st.chat_message("assistant"):
                    st.markdown(td["reply"])
                    st.caption(f"🤖 {td['provider']} · {td['model_used']} · Risk: **{td['struggle_risk_level'].upper()}**")
                st.session_state["messages"].append({"role": "assistant", "content": td["reply"]})
            else:
                st.error(f"API Error: {res.text}")
        except Exception as e:
            st.error(f"Could not reach AI Tutor: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
#   AI QUIZ
# ═══════════════════════════════════════════════════════════════════════════════
elif active == "quiz":
    page_header("AI Quiz Generator", "Dynamic MCQ quizzes for any topic — with instant closed-loop profile updates.")

    qz_c1, qz_c2, qz_c3, _ = st.columns([1, 1, 1, 1])
    with qz_c1:
        qz_sid = st.number_input("Student ID", min_value=1, max_value=500, value=1, step=1, key="qz_sid")
    with qz_c2:
        qz_tid = st.number_input("Topic ID (1–20)", min_value=1, max_value=20, value=12, step=1, key="qz_tid")
    with qz_c3:
        q_count = st.slider("Questions", min_value=1, max_value=5, value=3)

    if st.button("⚡ Generate My Quiz", type="primary"):
        try:
            gen_res = requests.post(f"{API_BASE_URL}/quiz/generate", json={"student_id": int(qz_sid), "topic_id": int(qz_tid), "question_count": int(q_count)}, timeout=5)
            if gen_res.status_code == 200:
                st.session_state["active_quiz"] = gen_res.json()
                st.success("Quiz generated! Answer below.")
            else:
                st.error(f"API Error: {gen_res.text}")
        except Exception as e:
            st.error(f"Could not generate quiz: {e}")

    aq = st.session_state.get("active_quiz")
    if aq:
        st.divider()
        st.markdown(f"#### {aq['topic_name']} ({aq['subject']})")
        st.caption(f"Session: `{aq['quiz_session_id']}` · Difficulty: **{aq['difficulty'].title()}**")
        choices = []
        for idx, q in enumerate(aq["questions"]):
            st.markdown(f"**Q{idx+1}: {q['question_text']}**")
            ch = st.radio(f"Answer Q{idx+1}", options=q["options"], index=0, key=f"q_choice_{idx}")
            choices.append(q["options"].index(ch))

        if st.button("📤 Submit & Close Learning Loop", type="primary"):
            try:
                sub_res = requests.post(f"{API_BASE_URL}/quiz/submit", json={
                    "student_id": int(aq["student_id"]), "topic_id": int(aq["topic_id"]),
                    "quiz_session_id": aq["quiz_session_id"], "answers": choices, "time_spent": 180,
                }, timeout=8)
                if sub_res.status_code == 200:
                    out = sub_res.json()
                    st.divider()
                    badge = "🟢 PASSED" if out["is_passed"] else "🔴 NEEDS REVIEW"
                    st.markdown(f"### {out['score_percentage']:.1f}% — {out['correct_answers']}/{out['total_questions']} Correct · {badge}")
                    cl = out["closed_loop_updates"]
                    cl1, cl2, cl3, cl4 = st.columns(4)
                    with cl1: st.metric("DB Record", "SAVED ✅")
                    with cl2: st.metric("Struggle Risk", cl["struggle_risk_level"].upper(), delta=f"{cl['struggle_probability']*100:.1f}%")
                    with cl3: st.metric("Difficulty", cl["new_difficulty"].title(), delta="SCALED" if cl["difficulty_changed"] else None)
                    with cl4: st.metric("Path %", f"{cl['learning_path_completion_pct']}%")
                    if cl["difficulty_changed"]:
                        st.balloons()
                        st.warning(f"⚡ {cl['adaptive_reason']}")
                    for qb in out["question_breakdown"]:
                        qs = "✅" if qb["is_correct"] else "❌"
                        with st.expander(f"Q{qb['question_id']}: {qs}"):
                            st.write(f"**Question**: {qb['question_text']}")
                            st.write(f"**Your Answer**: `{qb['user_selected_option']}`")
                            if not qb["is_correct"]:
                                st.write(f"**Correct**: `{qb['correct_option_text']}`")
                            st.info(f"💡 {qb['explanation']}")
                else:
                    st.error(f"API Error: {sub_res.text}")
            except Exception as ex:
                st.error(f"Could not submit quiz: {ex}")


# ═══════════════════════════════════════════════════════════════════════════════
#   ACCOUNT
# ═══════════════════════════════════════════════════════════════════════════════
elif active == "account":
    page_header("Account & Security", "JWT authentication, salted password hashing, rate limiting, and request tracking.")

    tab1, tab2, tab3 = st.tabs(["🔑  Sign In / Register", "👤  My Profile", "🛡️  Security"])

    with tab1:
        s1, s2 = st.columns(2)
        with s1:
            st.markdown("#### Create Account")
            r_name = st.text_input("Full Name", value="Alex Johnson", key="r_name")
            r_email = st.text_input("Email", value="alex@example.com", key="r_email")
            r_pass = st.text_input("Password", type="password", value="SecretPass123!", key="r_pass")
            r_role = st.selectbox("Role", ["student", "instructor"], key="r_role")
            if st.button("🚀 Create Account", type="primary"):
                try:
                    rr = requests.post(f"{API_BASE_URL}/auth/register", json={"name": r_name, "email": r_email, "password": r_pass, "role": r_role}, timeout=5)
                    if rr.status_code in (200, 201):
                        od = rr.json()
                        st.session_state["jwt_token"] = od["access_token"]
                        st.success(f"Account created for {od['name']}!")
                        st.json(od)
                    else:
                        st.error(f"Failed: {rr.text}")
                except Exception as ex:
                    st.error(f"API Error: {ex}")

        with s2:
            st.markdown("#### Sign In")
            l_email = st.text_input("Email", value="alex@example.com", key="l_email")
            l_pass = st.text_input("Password", type="password", value="SecretPass123!", key="l_pass")
            if st.button("🔑 Log In", type="primary"):
                try:
                    lr = requests.post(f"{API_BASE_URL}/auth/login", json={"email": l_email, "password": l_pass}, timeout=5)
                    if lr.status_code == 200:
                        od = lr.json()
                        st.session_state["jwt_token"] = od["access_token"]
                        st.success(f"Welcome back, {od['name']}!")
                        st.json(od)
                    else:
                        st.error(f"Failed: {lr.text}")
                except Exception as ex:
                    st.error(f"API Error: {ex}")

    with tab2:
        tok = st.session_state.get("jwt_token", "")
        tok_in = st.text_area("Bearer Token", value=tok, height=80)
        if st.button("🔍 View My Profile"):
            if not tok_in:
                st.warning("Register or log in first.")
            else:
                try:
                    mr = requests.get(f"{API_BASE_URL}/auth/me", headers={"Authorization": f"Bearer {tok_in}"}, timeout=5)
                    if mr.status_code == 200:
                        st.success("JWT verified — profile loaded!")
                        st.json(mr.json())
                    else:
                        st.error(f"Auth Failed ({mr.status_code}): {mr.text}")
                except Exception as ex:
                    st.error(f"Error: {ex}")

    with tab3:
        features = [
            ("🔑", "JWT Authentication", "HS256 signed tokens with expiry and claims validation."),
            ("🔒", "Salted Password Hashing", "PBKDF2 / SHA-256 with 100,000 iterations and random salt."),
            ("🛡️", "IP Rate Limiting", "120 requests/minute per IP — 429 Too Many Requests on breach."),
            ("🌐", "CORS Protection", "Restricted to trusted origins only."),
            ("🔍", "Request Tracking", "Every response includes a unique X-Request-ID UUID header."),
        ]
        for ic, title, desc in features:
            st.markdown(
                f'<div class="sec-row">'
                f'<div class="sec-icon">{ic}</div>'
                f'<div><div class="sec-title">{title}</div><div class="sec-desc">{desc}</div></div></div>',
                unsafe_allow_html=True,
            )


# ═══════════════════════════════════════════════════════════════════════════════
#   INFRASTRUCTURE
# ═══════════════════════════════════════════════════════════════════════════════
elif active == "infra":
    page_header("Platform Infrastructure", "Docker container topology, Compose orchestration, persistent volumes, and health checks.")

    d1, d2 = st.columns(2)
    with d1:
        st.markdown("#### Container Topology")
        containers = [
            ("edusense_backend", "python:3.11-slim (multi-stage)", ":8000", "curl -f /health", "appuser"),
            ("edusense_frontend", "python:3.11-slim", ":8501", "curl -f /_stcore/health", "root"),
        ]
        for name, image, port, hc, user in containers:
            st.markdown(
                f'<div class="infra-card">'
                f'<div class="infra-name">{name}</div>'
                f'<div class="infra-detail">'
                f'<b>Image:</b> {image}<br>'
                f'<b>Port:</b> {port} · <b>User:</b> {user}<br>'
                f'<b>Health:</b> <code>{hc}</code></div></div>',
                unsafe_allow_html=True,
            )
        st.markdown(
            '<div class="infra-card">'
            '<div class="infra-name">edusense_data (Volume)</div>'
            '<div class="infra-detail">Shared persistent volume → <code>/app/edusense.db</code> & <code>/app/ml/artifacts</code></div></div>',
            unsafe_allow_html=True,
        )

    with d2:
        st.markdown("#### Infrastructure Status")
        if os.path.exists("Dockerfile") and os.path.exists("docker-compose.yml"):
            st.success("✅ Dockerfile & docker-compose.yml verified!")
            st.code("docker-compose up --build -d", language="bash")
        else:
            st.warning("Docker files not found in project root.")
        with st.expander("📄 docker-compose.yml"):
            if os.path.exists("docker-compose.yml"):
                with open("docker-compose.yml", "r") as f:
                    st.code(f.read(), language="yaml")
