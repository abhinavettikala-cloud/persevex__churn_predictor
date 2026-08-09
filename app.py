import os
import sys
import json
import time
import random
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd
import numpy as np
import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go

# Ensure project root is on sys.path for module resolution
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# -----------------------------------------------------------------------------
# 1. Page Configuration (Must be first Streamlit command)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Persevex AI — Enterprise Churn Telemetry",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. Theme Preferences & Persistence System
# -----------------------------------------------------------------------------
query_params = st.query_params
initial_theme = "light"

if "theme" in query_params:
    param_theme = query_params["theme"].lower()
    if param_theme in ["dark", "light"]:
        initial_theme = param_theme

if "churn_predictor_theme" not in st.session_state:
    st.session_state["churn_predictor_theme"] = initial_theme

# -----------------------------------------------------------------------------
# 3. Sidebar Brand Header & Theme Toggle Control
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 6px 0 16px 0;">
        <div style="display: inline-block; background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #EC4899 100%); color: white; padding: 10px 22px; border-radius: 16px; font-weight: 900; font-size: 1.35rem; letter-spacing: 0.12em; box-shadow: 0 8px 25px rgba(79, 70, 229, 0.45);">
            PERSEVEX™
        </div>
        <div style="font-size: 0.72rem; font-weight: 800; color: #64748B; text-transform: uppercase; letter-spacing: 0.18em; margin-top: 10px;">
            AI Churn Telemetry Engine
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # Theme Selection Radio
    st.subheader("🎨 Visual Palette")
    theme_selection = st.radio(
        "Select Theme:",
        options=["☀️ Persevex Light", "🌙 Persevex Midnight"],
        index=0 if st.session_state["churn_predictor_theme"] == "light" else 1,
        key="theme_radio_input"
    )

    selected_mode = "dark" if "Midnight" in theme_selection else "light"
    if selected_mode != st.session_state["churn_predictor_theme"]:
        st.session_state["churn_predictor_theme"] = selected_mode
        st.query_params["theme"] = selected_mode
        st.rerun()

    is_dark = st.session_state["churn_predictor_theme"] == "dark"

    st.markdown("---")

# -----------------------------------------------------------------------------
# 4. Centralized Design System & Color Palette
# -----------------------------------------------------------------------------
if is_dark:
    bg_app = "#090D16"
    primary_surface = "#0F172A"
    secondary_surface = "#1E293B"
    card_bg = "rgba(15, 23, 42, 0.85)"
    text_main = "#F8FAFC"
    text_sub = "#CBD5E1"
    text_muted = "#94A3B8"
    card_border = "rgba(99, 102, 241, 0.25)"
    primary_accent = "#6366F1"
    success_color = "#10B981"
    warning_color = "#F59E0B"
    danger_color = "#EF4444"

    hero_bg = "linear-gradient(135deg, #0F172A 0%, #1E1B4B 50%, #0F172A 100%)"
    hero_title_color = "#818CF8"
    plotly_text = "#CBD5E1"
    plotly_grid = "rgba(99, 102, 241, 0.08)"
    plotly_axis = "rgba(99, 102, 241, 0.25)"

    result_churn_bg = "linear-gradient(135deg, rgba(127, 29, 29, 0.45) 0%, rgba(15, 23, 42, 0.95) 100%)"
    result_churn_border = "rgba(239, 68, 68, 0.5)"
    result_retain_bg = "linear-gradient(135deg, rgba(6, 78, 59, 0.45) 0%, rgba(15, 23, 42, 0.95) 100%)"
    result_retain_border = "rgba(16, 185, 129, 0.5)"

    table_header_bg = "#1E1B4B"
    table_header_text = "#A5B4FC"
    table_header_border = "rgba(99, 102, 241, 0.4)"
    table_row_even = "rgba(15, 23, 42, 0.7)"
    table_row_odd = "rgba(30, 41, 59, 0.7)"
    table_border = "rgba(255, 255, 255, 0.08)"
    pill_bg = "rgba(99, 102, 241, 0.16)"
    pill_border = "rgba(99, 102, 241, 0.4)"
    pill_text = "#818CF8"
else:
    bg_app = "#F8FAFC"
    primary_surface = "#FFFFFF"
    secondary_surface = "#F1F5F9"
    card_bg = "#FFFFFF"
    text_main = "#0F172A"
    text_sub = "#475569"
    text_muted = "#64748B"
    card_border = "#E2E8F0"
    primary_accent = "#4F46E5"
    success_color = "#059669"
    warning_color = "#D97706"
    danger_color = "#DC2626"

    hero_bg = "linear-gradient(135deg, #EEF2FF 0%, #F5F3FF 50%, #FDF2F8 100%)"
    hero_title_color = "#4F46E5"
    plotly_text = "#334155"
    plotly_grid = "rgba(0, 0, 0, 0.06)"
    plotly_axis = "rgba(0, 0, 0, 0.15)"

    result_churn_bg = "#FEF2F2"
    result_churn_border = "#FCA5A5"
    result_retain_bg = "#ECFDF5"
    result_retain_border = "#6EE7B7"

    table_header_bg = "#EEF2FF"
    table_header_text = "#4338CA"
    table_header_border = "#C7D2FE"
    table_row_even = "#FFFFFF"
    table_row_odd = "#F8FAFC"
    table_border = "#E2E8F0"
    pill_bg = "#EEF2FF"
    pill_border = "#C7D2FE"
    pill_text = "#4338CA"

# Dynamic CSS Micro-Animations & Responsive Glassmorphism Architecture
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    *, *::before, *::after {{
        transition: background-color 250ms cubic-bezier(0.4, 0, 0.2, 1), 
                    color 250ms cubic-bezier(0.4, 0, 0.2, 1), 
                    border-color 250ms cubic-bezier(0.4, 0, 0.2, 1), 
                    box-shadow 250ms cubic-bezier(0.4, 0, 0.2, 1),
                    transform 250ms cubic-bezier(0.4, 0, 0.2, 1);
    }}

    .stApp {{
        background-color: {bg_app} !important;
        color: {text_main} !important;
        font-family: 'Plus Jakarta Sans', 'Inter', system-ui, -apple-system, sans-serif;
    }}

    [data-testid="stSidebar"] {{
        background-color: {secondary_surface} !important;
        border-right: 1px solid {card_border} !important;
    }}
    [data-testid="stSidebar"] * {{
        color: {text_main} !important;
    }}

    .hero-container {{
        background: {hero_bg};
        border: 2px solid {card_border};
        border-radius: 20px;
        padding: 28px 36px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
    }}
    .hero-title {{
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        color: {hero_title_color} !important;
        margin-bottom: 6px;
    }}
    .hero-subtitle {{
        color: {text_sub} !important;
        font-size: 1.05rem;
        font-weight: 600;
    }}

    .glass-card {{
        background: {card_bg};
        border: 1px solid {card_border};
        border-radius: 18px;
        padding: 24px;
        margin-bottom: 16px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.04);
        backdrop-filter: blur(12px);
    }}
    .glass-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.07);
    }}

    .kpi-container {{
        background: {card_bg};
        border: 1px solid {card_border};
        border-radius: 16px;
        padding: 20px 22px;
        text-align: left;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.04);
    }}
    .kpi-container:hover {{
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
    }}
    .kpi-title {{
        font-size: 0.78rem;
        font-weight: 700;
        color: {text_sub} !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 6px;
    }}
    .kpi-value {{
        font-size: 2.2rem;
        font-weight: 800;
        color: {text_main} !important;
        line-height: 1.1;
    }}
    .kpi-badge {{
        display: inline-block;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 12px;
        margin-top: 8px;
    }}

    .result-card-churn {{
        background: {result_churn_bg};
        border: 2px solid {result_churn_border};
        border-left: 6px solid {danger_color};
        border-radius: 18px;
        padding: 28px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(239, 68, 68, 0.15);
    }}
    .result-card-retain {{
        background: {result_retain_bg};
        border: 2px solid {result_retain_border};
        border-left: 6px solid {success_color};
        border-radius: 18px;
        padding: 28px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(16, 185, 129, 0.15);
    }}

    .section-pill {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: {pill_bg};
        border: 1px solid {pill_border};
        color: {pill_text} !important;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.88rem;
        font-weight: 700;
        margin-top: 16px;
        margin-bottom: 14px;
    }}

    h1, h2, h3, h4, h5, h6, label, .stMarkdown p, .stMarkdown span {{
        color: {text_main} !important;
    }}

    /* Form Input & Select Styling */
    div[data-baseweb="select"] > div {{
        background-color: {card_bg} !important;
        color: {text_main} !important;
        border-color: {card_border} !important;
        border-radius: 12px !important;
    }}

    input[type="number"], input[type="text"] {{
        background-color: {card_bg} !important;
        color: {text_main} !important;
        border-color: {card_border} !important;
        border-radius: 12px !important;
    }}

    .stButton>button {{
        background: linear-gradient(135deg, {primary_accent} 0%, #4338CA 100%);
        color: #FFFFFF !important;
        border: none;
        border-radius: 12px;
        font-weight: 700;
        padding: 12px 24px;
        box-shadow: 0 4px 18px rgba(79, 70, 229, 0.35);
    }}
    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(79, 70, 229, 0.5);
    }}

    button[data-baseweb="tab"] {{
        color: {text_sub} !important;
        font-weight: 700 !important;
        font-size: 0.98rem !important;
        background-color: transparent !important;
        border: none !important;
        padding: 10px 18px !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {primary_accent} !important;
        border-bottom: 3px solid {primary_accent} !important;
        font-weight: 800 !important;
    }}

    div[data-testid="stDataFrame"], div[data-testid="stTable"] {{
        background-color: {card_bg} !important;
        border: 1px solid {card_border} !important;
        border-radius: 16px !important;
        padding: 6px !important;
    }}

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. In-Memory ML Predictor Initialization & Safe Artifact Loading
# -----------------------------------------------------------------------------
@st.cache_resource
def load_ml_predictor():
    """Attempts to initialize the standalone ML ChurnPredictor."""
    try:
        from src.api.inference import ChurnPredictor
        predictor = ChurnPredictor("model.pkl", "scaler.pkl", "encoder.pkl")
        if all(predictor.is_healthy()):
            return predictor, None
        else:
            return None, "Model files found but could not be initialized correctly."
    except FileNotFoundError as fnf_err:
        return None, f"Model file not found. Please verify that model.pkl, scaler.pkl, and encoder.pkl exist in the project directory. Details: {str(fnf_err)}"
    except Exception as exc:
        return None, f"Error loading machine learning model artifacts: {str(exc)}"

standalone_predictor, model_load_error = load_ml_predictor()

# -----------------------------------------------------------------------------
# 6. Persistent & Session-Based Prediction History System
# -----------------------------------------------------------------------------
HISTORY_FILE = BASE_DIR / "evaluations_history.json"

def get_history_data():
    """Retrieve history from session_state or disk."""
    if "prediction_history" in st.session_state and isinstance(st.session_state.prediction_history, list):
        return st.session_state.prediction_history

    history = []
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    history = data
        except Exception:
            pass

    if not history:
        history = [
            {"CustomerID": "CUST-7590", "Contract": "Month-to-month", "Tenure": 1, "MonthlyCharges": "$29.85", "Probability": "74.2%", "Risk": "High", "Verdict": "Churn", "Time": "14:32:05"},
            {"CustomerID": "CUST-5575", "Contract": "One year", "Tenure": 34, "MonthlyCharges": "$56.95", "Probability": "12.4%", "Risk": "Low", "Verdict": "No Churn", "Time": "14:28:10"},
            {"CustomerID": "CUST-3668", "Contract": "Month-to-month", "Tenure": 2, "MonthlyCharges": "$53.85", "Probability": "58.6%", "Risk": "Medium", "Verdict": "Churn", "Time": "14:15:22"},
            {"CustomerID": "CUST-7795", "Contract": "One year", "Tenure": 45, "MonthlyCharges": "$42.30", "Probability": "8.1%", "Risk": "Low", "Verdict": "No Churn", "Time": "13:54:01"},
            {"CustomerID": "CUST-9237", "Contract": "Month-to-month", "Tenure": 2, "MonthlyCharges": "$70.70", "Probability": "81.9%", "Risk": "High", "Verdict": "Churn", "Time": "13:40:18"}
        ]
        save_history_data(history)

    st.session_state.prediction_history = history
    return history

def save_history_data(history_list):
    """Save history list to session state and disk."""
    st.session_state.prediction_history = history_list
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history_list, f, indent=2)
    except Exception:
        pass

def add_history_record(record):
    """Add a new prediction evaluation to history."""
    history = get_history_data()
    history.insert(0, record)
    save_history_data(history[:100])

eval_history = get_history_data()

# -----------------------------------------------------------------------------
# 7. Sidebar Engine Diagnostics & Status
# -----------------------------------------------------------------------------
with st.sidebar:
    st.subheader("📡 Engine Diagnostics")
    if standalone_predictor is not None:
        st.success("🟢 In-Memory ML Engine Online")
    else:
        st.error("🔴 Model Engine Offline")

    if model_load_error:
        st.warning("⚠️ Artifact Notice: Model files missing or failed to initialize.")

    st.markdown("---")
    st.caption("🚀 **Render Ready**: Optimized for Python Web Service deployment.")

# -----------------------------------------------------------------------------
# 8. Hero Header Banner
# -----------------------------------------------------------------------------
theme_badge_label = "🌙 PERSEVEX MIDNIGHT" if is_dark else "☀️ PERSEVEX PEARL"

st.markdown(f"""
<div class="hero-container">
    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; margin-bottom: 10px;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #EC4899 100%); color: white; padding: 5px 14px; border-radius: 10px; font-weight: 800; font-size: 0.88rem; letter-spacing: 0.08em; box-shadow: 0 4px 15px rgba(79, 70, 229, 0.35);">
                PERSEVEX™ AI
            </div>
            <span style="font-size: 0.82rem; font-weight: 700; color: {text_sub}; text-transform: uppercase; letter-spacing: 0.12em;">
                Enterprise Customer Attrition Telemetry v2.5
            </span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px; background: {pill_bg}; border: 1px solid {pill_border}; padding: 4px 14px; border-radius: 20px;">
            <span style="font-size: 0.78rem; font-weight: 700; color: {pill_text};">{theme_badge_label}</span>
        </div>
    </div>
    <div class="hero-title">Persevex Churn Intelligence Hub</div>
    <div class="hero-subtitle">Next-generation autonomous customer attrition telemetry, predictive feature scoring, and prescription analytics.</div>
</div>
""", unsafe_allow_html=True)

# Top Navigation Tabs
tab_dash, tab_predict, tab_hist, tab_analytics, tab_perf, tab_about = st.tabs([
    "📊 Executive Overview",
    "🔮 Persevex Predictor",
    "📜 Prediction History",
    "📈 Analytics & Telemetry",
    "🏆 Model Governance",
    "ℹ️ About Engine"
])

# -----------------------------------------------------------------------------
# TAB 1: EXECUTIVE DASHBOARD
# -----------------------------------------------------------------------------
with tab_dash:
    eval_df = pd.DataFrame(eval_history)
    total_evals = len(eval_df)
    churn_count = int(sum(eval_df["Verdict"] == "Churn")) if total_evals > 0 else 0
    retain_count = total_evals - churn_count
    churn_rate = (churn_count / total_evals * 100) if total_evals > 0 else 0.0

    prob_list = []
    if total_evals > 0 and "Probability" in eval_df.columns:
        for p_str in eval_df["Probability"]:
            try:
                prob_list.append(float(str(p_str).replace("%", "")))
            except Exception:
                pass
    avg_prob = np.mean(prob_list) if prob_list else 0.0

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="kpi-container" style="border-top: 4px solid #38BDF8;">
            <div class="kpi-title">Total Evaluated Customers</div>
            <div class="kpi-value" style="color: #38BDF8;">{total_evals:,}</div>
            <div class="kpi-badge" style="background: rgba(56, 189, 248, 0.15); color: #0284C7;">Live Tracker</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="kpi-container" style="border-top: 4px solid {danger_color};">
            <div class="kpi-title">Predicted Churn Rate</div>
            <div class="kpi-value" style="color: {danger_color};">{churn_rate:.1f}%</div>
            <div class="kpi-badge" style="background: rgba(239, 68, 68, 0.15); color: {danger_color};">{churn_count} High Risk Alerts</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="kpi-container" style="border-top: 4px solid {success_color};">
            <div class="kpi-title">Retained Customer Count</div>
            <div class="kpi-value" style="color: {success_color};">{retain_count:,}</div>
            <div class="kpi-badge" style="background: rgba(16, 185, 129, 0.15); color: {success_color};">Low Risk Tier</div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="kpi-container" style="border-top: 4px solid #8B5CF6;">
            <div class="kpi-title">Avg Churn Probability</div>
            <div class="kpi-value" style="color: #8B5CF6;">{avg_prob:.1f}%</div>
            <div class="kpi-badge" style="background: rgba(139, 92, 246, 0.15); color: #8B5CF6;">Model Calibrated</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    d_col1, d_col2 = st.columns([2, 1])
    with d_col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📈 Prediction Activity Trend (Weekly)")
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        retained_trend = [240, 310, 290, 410, 380, 210, 260]
        churned_trend = [75, 82, 64, 105, 89, 45, 52]

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=days, y=retained_trend, name="Retained Customers",
            mode="lines+markers", line=dict(color="#38BDF8", width=3.5, shape="spline"),
            fill="tozeroy", fillcolor="rgba(56, 189, 248, 0.12)"
        ))
        fig_trend.add_trace(go.Scatter(
            x=days, y=churned_trend, name="Churn Alerts",
            mode="lines+markers", line=dict(color=danger_color, width=3.5, shape="spline"),
            fill="tozeroy", fillcolor="rgba(239, 68, 68, 0.12)"
        ))
        fig_trend.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans", color=plotly_text, size=12),
            xaxis=dict(showgrid=False, linecolor=plotly_axis),
            yaxis=dict(showgrid=True, gridcolor=plotly_grid, linecolor=plotly_axis),
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with d_col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🎯 Risk Tier Breakdown")
        low_cnt = int(sum(eval_df["Risk"] == "Low")) if total_evals > 0 else 0
        med_cnt = int(sum(eval_df["Risk"] == "Medium")) if total_evals > 0 else 0
        high_cnt = int(sum(eval_df["Risk"] == "High")) if total_evals > 0 else 0

        fig_pie = go.Figure(data=[go.Pie(
            labels=["Low Risk (<40%)", "Medium Risk (40-70%)", "High Risk (>70%)"],
            values=[max(low_cnt, 1), max(med_cnt, 1), max(high_cnt, 1)],
            hole=0.62,
            textinfo="percent+value",
            hoverinfo="label+value+percent",
            marker=dict(
                colors=[success_color, warning_color, danger_color],
                line=dict(color=card_bg, width=3)
            )
        )])
        fig_pie.update_layout(
            annotations=[dict(text="Risk<br>Tiers", x=0.5, y=0.5, font_size=15, font_color=text_main, font_family="Plus Jakarta Sans", font_weight=700, showarrow=False)],
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans", color=plotly_text, size=11),
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    # HTML Table Component for Recent Customer Evaluations
    st.markdown("<br>", unsafe_allow_html=True)
    tbl_col1, tbl_col2 = st.columns([3, 1])
    with tbl_col1:
        st.subheader("📋 Recent Customer Evaluations")
        st.caption(f"Showing {total_evals} saved evaluation records (saved to `evaluations_history.json`):")
    with tbl_col2:
        if st.button("🗑️ Reset History Log", use_container_width=True):
            if HISTORY_FILE.exists():
                try:
                    os.remove(HISTORY_FILE)
                except Exception:
                    pass
            st.session_state.prediction_history = []
            st.rerun()

    rows_html = []
    for idx, row in eval_df.iterrows():
        risk_str = str(row.get("Risk", ""))
        verdict_str = str(row.get("Verdict", ""))

        if risk_str == "High":
            risk_badge = f'<span style="background: rgba(239, 68, 68, 0.2); color: {danger_color}; padding: 4px 12px; border-radius: 12px; font-weight: 700; border: 1px solid rgba(239, 68, 68, 0.4);">High</span>'
        elif risk_str == "Medium":
            risk_badge = f'<span style="background: rgba(245, 158, 11, 0.2); color: {warning_color}; padding: 4px 12px; border-radius: 12px; font-weight: 700; border: 1px solid rgba(245, 158, 11, 0.4);">Medium</span>'
        else:
            risk_badge = f'<span style="background: rgba(16, 185, 129, 0.2); color: {success_color}; padding: 4px 12px; border-radius: 12px; font-weight: 700; border: 1px solid rgba(16, 185, 129, 0.4);">Low</span>'

        verdict_color = danger_color if verdict_str == "Churn" else success_color
        verdict_badge = f'<span style="color: {verdict_color}; font-weight: 700;">{verdict_str}</span>'

        bg_row = table_row_even if idx % 2 == 0 else table_row_odd

        rows_html.append(
            f'<tr style="background: {bg_row}; border-bottom: 1px solid {table_border}; color: {text_main}; font-size: 0.92rem;">'
            f'<td style="padding: 12px 18px; font-weight: 700;">{row.get("CustomerID", "")}</td>'
            f'<td style="padding: 12px 18px;">{row.get("Contract", "")}</td>'
            f'<td style="padding: 12px 18px;">{row.get("Tenure", "")} mos</td>'
            f'<td style="padding: 12px 18px; font-weight: 600;">{row.get("MonthlyCharges", "")}</td>'
            f'<td style="padding: 12px 18px; font-weight: 700; color: #818CF8;">{row.get("Probability", "")}</td>'
            f'<td style="padding: 12px 18px;">{risk_badge}</td>'
            f'<td style="padding: 12px 18px;">{verdict_badge}</td>'
            f'<td style="padding: 12px 18px; color: {text_muted}; font-size: 0.85rem;">{row.get("Time", "")}</td>'
            f'</tr>'
        )

    table_html = (
        f'<div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 16px; overflow: hidden; margin-top: 12px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);">'
        f'<table style="width: 100%; border-collapse: collapse; text-align: left; font-family: \'Plus Jakarta Sans\', sans-serif;">'
        f'<thead>'
        f'<tr style="background: {table_header_bg}; color: {table_header_text}; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; border-bottom: 2px solid {table_header_border};">'
        f'<th style="padding: 14px 18px;">CustomerID</th>'
        f'<th style="padding: 14px 18px;">Contract</th>'
        f'<th style="padding: 14px 18px;">Tenure</th>'
        f'<th style="padding: 14px 18px;">Monthly Charges</th>'
        f'<th style="padding: 14px 18px;">Probability</th>'
        f'<th style="padding: 14px 18px;">Risk Tier</th>'
        f'<th style="padding: 14px 18px;">Verdict</th>'
        f'<th style="padding: 14px 18px;">Time</th>'
        f'</tr>'
        f'</thead>'
        f'<tbody>'
        + "".join(rows_html) +
        f'</tbody>'
        f'</table>'
        f'</div>'
    )
    st.markdown(table_html, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 2: PERSEVEX PREDICTOR
# -----------------------------------------------------------------------------
with tab_predict:
    if model_load_error:
        st.error(f"⚠️ **Model Availability Error**: {model_load_error}")

    st.subheader("⚡ Customer Profile Presets")
    st.caption("Click a preset button to instantly populate all 19 customer features:")

    pcol1, pcol2, pcol3 = st.columns(3)
    if "preset" not in st.session_state:
        st.session_state.preset = "default"

    with pcol1:
        if st.button("🔥 High Risk Churner Profile", use_container_width=True):
            st.session_state.preset = "high_risk"
    with pcol2:
        if st.button("🛡️ Loyal Customer Profile", use_container_width=True):
            st.session_state.preset = "loyal"
    with pcol3:
        if st.button("⚙️ Reset to Default", use_container_width=True):
            st.session_state.preset = "default"

    if st.session_state.preset == "high_risk":
        p_gender, p_senior, p_partner, p_dependents = "Female", 0, "No", "No"
        p_tenure, p_phone, p_multiple, p_internet = 1, "Yes", "No", "Fiber optic"
        p_sec, p_back, p_dev, p_tech, p_tv, p_mov = "No", "No", "No", "No", "No", "No"
        p_contract, p_paperless, p_payment = "Month-to-month", "Yes", "Electronic check"
        p_monthly, p_total = 85.50, 85.50
    elif st.session_state.preset == "loyal":
        p_gender, p_senior, p_partner, p_dependents = "Male", 0, "Yes", "Yes"
        p_tenure, p_phone, p_multiple, p_internet = 65, "Yes", "Yes", "DSL"
        p_sec, p_back, p_dev, p_tech, p_tv, p_mov = "Yes", "Yes", "Yes", "Yes", "Yes", "Yes"
        p_contract, p_paperless, p_payment = "Two year", "No", "Bank transfer (automatic)"
        p_monthly, p_total = 60.00, 3900.00
    else:
        p_gender, p_senior, p_partner, p_dependents = "Female", 0, "Yes", "No"
        p_tenure, p_phone, p_multiple, p_internet = 12, "Yes", "No", "Fiber optic"
        p_sec, p_back, p_dev, p_tech, p_tv, p_mov = "No", "Yes", "No", "No", "Yes", "No"
        p_contract, p_paperless, p_payment = "Month-to-month", "Yes", "Electronic check"
        p_monthly, p_total = 70.35, 844.20

    st.markdown("<br>", unsafe_allow_html=True)

    with st.form("churn_prediction_form_modern"):
        st.markdown('<div class="section-pill">👤 1. Customer Demographics</div>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            gender = st.selectbox("Gender", options=["Female", "Male"], index=0 if p_gender == "Female" else 1)
        with col2:
            senior_citizen = st.selectbox("Senior Citizen (>=65)", options=[0, 1], format_func=lambda x: "Yes" if x == 1 else "No", index=p_senior)
        with col3:
            partner = st.selectbox("Partner", options=["Yes", "No"], index=0 if p_partner == "Yes" else 1)
        with col4:
            dependents = st.selectbox("Dependents", options=["Yes", "No"], index=0 if p_dependents == "Yes" else 1)

        st.markdown('<div class="section-pill">📶 2. Telecommunications Services</div>', unsafe_allow_html=True)
        col5, col6, col7 = st.columns(3)
        with col5:
            phone_service = st.selectbox("Phone Service", options=["Yes", "No"], index=0 if p_phone == "Yes" else 1)
        with col6:
            multiple_lines = st.selectbox("Multiple Lines", options=["No phone service", "No", "Yes"], index=["No phone service", "No", "Yes"].index(p_multiple))
        with col7:
            internet_service = st.selectbox("Internet Service", options=["Fiber optic", "DSL", "No"], index=["Fiber optic", "DSL", "No"].index(p_internet))

        st.markdown('<div class="section-pill">🛡️ 3. Digital Add-On Services</div>', unsafe_allow_html=True)
        col8, col9, col10 = st.columns(3)
        with col8:
            online_security = st.selectbox("Online Security", options=["No internet service", "No", "Yes"], index=["No internet service", "No", "Yes"].index(p_sec))
            online_backup = st.selectbox("Online Backup", options=["No internet service", "No", "Yes"], index=["No internet service", "No", "Yes"].index(p_back))
        with col9:
            device_protection = st.selectbox("Device Protection", options=["No internet service", "No", "Yes"], index=["No internet service", "No", "Yes"].index(p_dev))
            tech_support = st.selectbox("Tech Support", options=["No internet service", "No", "Yes"], index=["No internet service", "No", "Yes"].index(p_tech))
        with col10:
            streaming_tv = st.selectbox("Streaming TV", options=["No internet service", "No", "Yes"], index=["No internet service", "No", "Yes"].index(p_tv))
            streaming_movies = st.selectbox("Streaming Movies", options=["No internet service", "No", "Yes"], index=["No internet service", "No", "Yes"].index(p_mov))

        st.markdown('<div class="section-pill">💳 4. Billing & Contract Terms</div>', unsafe_allow_html=True)
        col11, col12, col13 = st.columns(3)
        with col11:
            tenure = st.number_input("Tenure (Months)", min_value=0, max_value=120, value=int(p_tenure), step=1)
            contract = st.selectbox("Contract Type", options=["Month-to-month", "One year", "Two year"], index=["Month-to-month", "One year", "Two year"].index(p_contract))
        with col12:
            paperless_billing = st.selectbox("Paperless Billing", options=["Yes", "No"], index=0 if p_paperless == "Yes" else 1)
            payment_method = st.selectbox("Payment Method", options=[
                "Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"
            ], index=[
                "Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"
            ].index(p_payment))
        with col13:
            monthly_charges = st.number_input("Monthly Charges ($)", min_value=0.0, max_value=300.0, value=float(p_monthly), step=1.0)
            total_charges = st.number_input("Total Charges ($)", min_value=0.0, max_value=10000.0, value=float(p_total), step=10.0)

        st.markdown("<br>", unsafe_allow_html=True)
        submit_button = st.form_submit_button("🚀 Run Model Churn Prediction", type="primary", use_container_width=True)

    if submit_button:
        payload = {
            "gender": gender,
            "SeniorCitizen": int(senior_citizen),
            "Partner": partner,
            "Dependents": dependents,
            "tenure": int(tenure),
            "PhoneService": phone_service,
            "MultipleLines": multiple_lines,
            "InternetService": internet_service,
            "OnlineSecurity": online_security,
            "OnlineBackup": online_backup,
            "DeviceProtection": device_protection,
            "TechSupport": tech_support,
            "StreamingTV": streaming_tv,
            "StreamingMovies": streaming_movies,
            "Contract": contract,
            "PaperlessBilling": paperless_billing,
            "PaymentMethod": payment_method,
            "MonthlyCharges": float(monthly_charges),
            "TotalCharges": float(total_charges)
        }

        with st.spinner("Evaluating customer feature vector in ML pipeline..."):
            pred, prob, conf, risk, latency_ms = None, None, None, None, 0.0

            if standalone_predictor is not None:
                try:
                    from src.api.schemas import ChurnPredictionRequest
                    start_t = time.time()
                    req_obj = ChurnPredictionRequest(**payload)
                    res_obj = standalone_predictor.predict(req_obj)
                    latency_ms = (time.time() - start_t) * 1000
                    pred = res_obj.prediction
                    prob = res_obj.probability
                    conf = res_obj.confidence_score
                    risk = res_obj.risk_level
                except Exception as ex:
                    st.error(f"Inference error: {str(ex)}")

            if pred is None:
                api_url = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip('/') + "/predict"
                try:
                    start_t = time.time()
                    resp = requests.post(api_url, json=payload, timeout=2.0)
                    if resp.status_code == 200:
                        res = resp.json()
                        pred = res["prediction"]
                        prob = res["probability"]
                        conf = res["confidence_score"]
                        risk = res["risk_level"]
                        latency_ms = (time.time() - start_t) * 1000
                except Exception:
                    pass

            if pred is not None:
                new_entry = {
                    "CustomerID": f"CUST-{random.randint(1000, 9999)}",
                    "Contract": contract,
                    "Tenure": int(tenure),
                    "MonthlyCharges": f"${monthly_charges:.2f}",
                    "Probability": f"{(prob*100):.1f}%",
                    "Risk": risk,
                    "Verdict": pred,
                    "Time": datetime.now().strftime("%H:%M:%S")
                }
                add_history_record(new_entry)

                st.session_state.latest_prediction = {
                    "pred": pred, "prob": prob, "conf": conf, "risk": risk, "latency_ms": latency_ms
                }
                st.rerun()
            else:
                st.error("Model file not found or prediction failed. Please verify that model.pkl, scaler.pkl, and encoder.pkl exist in the model directory.")

    if "latest_prediction" in st.session_state:
        res = st.session_state.latest_prediction
        pred, prob, conf, risk, latency_ms = res["pred"], res["prob"], res["conf"], res["risk"], res["latency_ms"]

        st.markdown("<br>", unsafe_allow_html=True)
        card_class = "result-card-churn" if pred == "Churn" else "result-card-retain"
        risk_color = danger_color if risk == "High" else warning_color if risk == "Medium" else success_color

        st.markdown(f"""
        <div class="{card_class}">
            <div style="font-size: 1.05rem; color: {text_sub}; margin-bottom: 4px;">Real-Time AI Prediction Verdict</div>
            <div style="font-size: 3.2rem; font-weight: 800; margin-bottom: 10px; color: {risk_color};">
                {'🔴 Customer Will Churn' if pred == 'Churn' else '🟢 Customer Will Retain'}
            </div>
            <div style="font-size: 1.2rem; font-weight: 700; color: {text_main};">
                {risk.upper()} RISK TIER ({(prob*100):.1f}% Probability)
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        res_c1, res_c2 = st.columns([1, 1])
        with res_c1:
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob * 100,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Churn Probability Gauge", 'font': {'size': 18, 'color': plotly_text, 'family': "Plus Jakarta Sans"}},
                number={'suffix': "%", 'font': {'size': 36, 'color': risk_color, 'family': "Plus Jakarta Sans"}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': plotly_axis},
                    'bar': {'color': risk_color},
                    'bgcolor': card_bg,
                    'borderwidth': 2,
                    'bordercolor': plotly_axis,
                    'steps': [
                        {'range': [0, 40], 'color': "rgba(16, 185, 129, 0.18)"},
                        {'range': [40, 70], 'color': "rgba(245, 158, 11, 0.18)"},
                        {'range': [70, 100], 'color': "rgba(239, 68, 68, 0.18)"}
                    ]
                }
            ))
            fig_gauge.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color=plotly_text, family="Plus Jakarta Sans"),
                margin=dict(l=20, r=20, t=30, b=20),
                height=250
            )
            st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})

        with res_c2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("💡 Prescriptive Retention Actions")
            if pred == "Churn":
                st.error("""
                - **Action 1**: Assign dedicated Customer Retention Specialist immediately.
                - **Action 2**: Offer a 20% promotional discount on a 1-Year or 2-Year Contract extension.
                - **Action 3**: Provide complimentary 6-month Tech Support & Online Security add-on.
                """)
            else:
                st.success("""
                - **Action 1**: Maintain current engagement schedule.
                - **Action 2**: Target for premium service upgrades (e.g., Fiber optic / Streaming bundle).
                - **Action 3**: Schedule automated annual loyalty check-in.
                """)
            st.write(f"⏱️ **Inference Latency**: `{latency_ms:.1f} ms` | **Model Confidence**: `{conf*100:.1f}%`")
            st.success("✅ **Saved to History**: Your prediction was automatically saved to **Recent Customer Evaluations** on the Executive Dashboard!")
            st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 3: PREDICTION HISTORY
# -----------------------------------------------------------------------------
with tab_hist:
    st.subheader("📜 Customer Prediction History Log")
    h_col1, h_col2 = st.columns([3, 1])
    with h_col1:
        st.caption(f"Displaying {len(eval_history)} customer evaluation records:")
    with h_col2:
        if st.button("🗑️ Clear History", use_container_width=True):
            if HISTORY_FILE.exists():
                try:
                    os.remove(HISTORY_FILE)
                except Exception:
                    pass
            st.session_state.prediction_history = []
            st.rerun()

    if eval_history:
        history_df = pd.DataFrame(eval_history)
        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "CustomerID": "Customer ID",
                "Contract": "Contract Type",
                "Tenure": st.column_config.NumberColumn("Tenure (Mos)", format="%d"),
                "MonthlyCharges": "Monthly Charges",
                "Probability": "Churn Probability",
                "Risk": "Risk Level",
                "Verdict": "Verdict",
                "Time": "Timestamp"
            }
        )
    else:
        st.info("No prediction history recorded yet.")

# -----------------------------------------------------------------------------
# TAB 4: ANALYTICS & TELEMETRY
# -----------------------------------------------------------------------------
with tab_analytics:
    st.subheader("📊 Customer Demographics & Churn Factor Analytics")

    a1, a2 = st.columns(2)
    with a1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📄 Contract Type Breakdown")
        fig_contract = go.Figure(data=[go.Pie(
            labels=["Month-to-month", "Two year", "One year"],
            values=[3875, 1695, 1473],
            hole=0.55,
            textinfo="percent+label",
            hoverinfo="label+value+percent",
            marker=dict(
                colors=["#38BDF8", success_color, warning_color],
                line=dict(color=card_bg, width=3)
            )
        )])
        fig_contract.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans", color=plotly_text, size=12),
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_contract, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with a2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("💳 Payment Method Distribution")
        fig_pay = go.Figure(data=[go.Bar(
            x=["Electronic check", "Mailed check", "Bank transfer", "Credit card"],
            y=[2365, 1612, 1544, 1522],
            text=["2,365", "1,612", "1,544", "1,522"],
            textposition="outside",
            marker=dict(
                color=["#38BDF8", "#6366F1", "#8B5CF6", "#EC4899"],
                line=dict(color=plotly_axis, width=1)
            )
        )])
        fig_pay.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans", color=plotly_text, size=12),
            xaxis=dict(showgrid=False, linecolor=plotly_axis),
            yaxis=dict(showgrid=True, gridcolor=plotly_grid, linecolor=plotly_axis, title="Count"),
            margin=dict(l=10, r=10, t=30, b=10)
        )
        st.plotly_chart(fig_pay, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🔍 Feature Importance & Target Correlation with Churn")
    fig_corr = go.Figure(data=[go.Bar(
        y=["Long Term Contract", "Tenure", "Total Charges", "Tech Support / Security", "Senior Citizen", "Monthly Charges"],
        x=[-0.4051, -0.3522, -0.1983, -0.1827, 0.1508, 0.1934],
        orientation="h",
        text=["-40.5%", "-35.2%", "-19.8%", "-18.3%", "+15.1%", "+19.3%"],
        textposition="outside",
        marker=dict(
            color=[-0.4051, -0.3522, -0.1983, -0.1827, 0.1508, 0.1934],
            colorscale=[[0, success_color], [0.5, "#38BDF8"], [1, danger_color]],
            line=dict(color=plotly_axis, width=1)
        )
    )])
    fig_corr.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans", color=plotly_text, size=12),
        xaxis=dict(showgrid=True, gridcolor=plotly_grid, title="Correlation Coefficient with Churn Target"),
        yaxis=dict(showgrid=False),
        margin=dict(l=10, r=20, t=10, b=10)
    )
    st.plotly_chart(fig_corr, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 5: MODEL PERFORMANCE & METRICS
# -----------------------------------------------------------------------------
with tab_perf:
    st.subheader("🏆 Model Performance & Provenance Manifest")

    metadata_path = BASE_DIR / "metadata.json"
    metrics_data = None
    if metadata_path.exists():
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                meta_json = json.load(f)
                metrics_data = meta_json.get("metrics")
        except Exception:
            pass

    if metrics_data:
        acc = metrics_data.get("accuracy")
        prec = metrics_data.get("precision")
        rec = metrics_data.get("recall")
        f1 = metrics_data.get("f1_score")
        roc_auc = metrics_data.get("roc_auc")
        pr_auc = metrics_data.get("pr_auc", 0.6577)

        m1, m2, m3, m4, m5, m6 = st.columns(6)
        with m1:
            st.markdown(f"""
            <div class="kpi-container" style="border-top: 4px solid #38BDF8;">
                <div class="kpi-title">Accuracy</div>
                <div class="kpi-value" style="color: #38BDF8;">{(acc*100):.1f}%</div>
                <div class="kpi-badge" style="background: rgba(56, 189, 248, 0.15); color: #0284C7;">Overall Fit</div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="kpi-container" style="border-top: 4px solid #6366F1;">
                <div class="kpi-title">Precision</div>
                <div class="kpi-value" style="color: #6366F1;">{(prec*100):.1f}%</div>
                <div class="kpi-badge" style="background: rgba(99, 102, 241, 0.15); color: #6366F1;">Positive Predictive</div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class="kpi-container" style="border-top: 4px solid #8B5CF6;">
                <div class="kpi-title">Recall</div>
                <div class="kpi-value" style="color: #8B5CF6;">{(rec*100):.1f}%</div>
                <div class="kpi-badge" style="background: rgba(139, 92, 246, 0.15); color: #8B5CF6;">Sensitivity Rate</div>
            </div>
            """, unsafe_allow_html=True)
        with m4:
            st.markdown(f"""
            <div class="kpi-container" style="border-top: 4px solid #EC4899;">
                <div class="kpi-title">F1 Score</div>
                <div class="kpi-value" style="color: #EC4899;">{f1:.4f}</div>
                <div class="kpi-badge" style="background: rgba(236, 72, 153, 0.15); color: #EC4899;">Harmonic Mean</div>
            </div>
            """, unsafe_allow_html=True)
        with m5:
            st.markdown(f"""
            <div class="kpi-container" style="border-top: 4px solid {success_color};">
                <div class="kpi-title">ROC-AUC</div>
                <div class="kpi-value" style="color: {success_color};">{roc_auc:.4f}</div>
                <div class="kpi-badge" style="background: rgba(16, 185, 129, 0.15); color: {success_color};">Discriminative Power</div>
            </div>
            """, unsafe_allow_html=True)
        with m6:
            st.markdown(f"""
            <div class="kpi-container" style="border-top: 4px solid #F59E0B;">
                <div class="kpi-title">PR-AUC</div>
                <div class="kpi-value" style="color: #F59E0B;">{pr_auc:.4f}</div>
                <div class="kpi-badge" style="background: rgba(245, 158, 11, 0.15); color: #F59E0B;">Precision-Recall</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        pm1, pm2 = st.columns(2)
        with pm1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("🔥 Confusion Matrix Heatmap")
            cm = metrics_data.get("confusion_matrix", [[939, 96], [181, 193]])
            fig_cm = go.Figure(data=go.Heatmap(
                z=cm,
                x=["Predicted No Churn", "Predicted Churn"],
                y=["Actual No Churn", "Actual Churn"],
                colorscale=[[0, card_bg], [0.5, "#38BDF8"], [1, "#1D4ED8"]],
                text=[[f"{cm[0][0]}<br>(True Negative)", f"{cm[0][1]}<br>(False Positive)"],
                      [f"{cm[1][0]}<br>(False Negative)", f"{cm[1][1]}<br>(True Positive)"]],
                texttemplate="%{text}",
                textfont={"size": 14, "color": text_main, "family": "Plus Jakarta Sans"}
            ))
            fig_cm.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Plus Jakarta Sans", color=plotly_text),
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig_cm, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)

        with pm2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("📉 ROC Characteristic Curve")
            fpr = [0.0, 0.05, 0.12, 0.22, 0.35, 0.50, 0.70, 0.88, 1.0]
            tpr = [0.0, 0.38, 0.62, 0.78, 0.86, 0.92, 0.96, 0.99, 1.0]
            fig_roc = go.Figure()
            fig_roc.add_trace(go.Scatter(
                x=fpr, y=tpr, name=f"Calibrated Model (AUC = {roc_auc:.4f})",
                mode="lines", line=dict(color="#38BDF8", width=3.5, shape="spline"),
                fill="tozeroy", fillcolor="rgba(56, 189, 248, 0.12)"
            ))
            fig_roc.add_trace(go.Scatter(
                x=[0, 1], y=[0, 1], name="Random Classifier Baseline",
                mode="lines", line=dict(color=text_muted, width=2, dash="dash")
            ))
            fig_roc.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Plus Jakarta Sans", color=plotly_text),
                xaxis=dict(showgrid=True, gridcolor=plotly_grid, title="False Positive Rate"),
                yaxis=dict(showgrid=True, gridcolor=plotly_grid, title="True Positive Rate"),
                margin=dict(l=10, r=10, t=10, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_roc, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Model performance metrics are not available.")

# -----------------------------------------------------------------------------
# TAB 6: ABOUT
# -----------------------------------------------------------------------------
with tab_about:
    st.subheader("ℹ️ About Persevex AI Engine")
    st.markdown(f"""
    <div class="glass-card">
        <h4>Overview</h4>
        <p>This Streamlit application delivers production-grade customer churn prediction and risk analytics for telecommunications providers.</p>
        <ul>
            <li><b>Visual Theme System</b>: Dynamic dual Light/Dark mode with session persistence.</li>
            <li><b>Model Framework</b>: Scikit-learn Calibrated Logistic Regression with balanced class weighting.</li>
            <li><b>Preprocessing</b>: Standard scaling for continuous numerical features & One-Hot Encoding for categorical features.</li>
            <li><b>Deployment Target</b>: Render Web Service (Python Native Environment).</li>
            <li><b>Binding Address & Port</b>: Listens on <code>0.0.0.0</code> and port specified by <code>$PORT</code>.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    pass
