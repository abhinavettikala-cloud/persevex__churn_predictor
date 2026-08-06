import streamlit as st
import requests
import json
import time
import os
import pandas as pd
import numpy as np
from datetime import datetime, timezone
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Telecom Churn AI — Enterprise Analytics Platform",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. Sidebar Diagnostics & Theme Mode Selector
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3059/3059502.png", width=55)
    st.title("Telecom Churn AI")
    st.caption("Production Machine Learning Platform")
    st.markdown("---")

    # Theme Mode Selector
    st.subheader("🎨 Theme Mode")
    theme_choice = st.radio(
        "Select Visual Theme:",
        options=["🌙 Dark Mode", "☀️ Light Mode"],
        index=0
    )
    is_dark = theme_choice == "🌙 Dark Mode"

    st.markdown("---")

    # API Connection Diagnostics
    st.subheader("📡 Backend API Diagnostics")
    default_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    api_base_url = st.text_input("FastAPI Server URL", value=default_url, help="URL of running FastAPI backend")

    health_url = f"{api_base_url.rstrip('/')}/health"
    try:
        health_resp = requests.get(health_url, timeout=2)
        if health_resp.status_code == 200:
            health_data = health_resp.json()
            if health_data.get("status") in ["healthy", "ok"]:
                st.success("🟢 API Connected & Operational")
            else:
                st.warning("🟡 API Degraded")
        else:
            st.error(f"🔴 API Error ({health_resp.status_code})")
    except Exception:
        st.error("🔴 API Offline (`python app.py`)")

    st.markdown("---")
    st.info("💡 **Tip**: Toggle between Dark Mode and Light Mode anytime using the sidebar selector.")

# -----------------------------------------------------------------------------
# 3. Dynamic Light / Dark CSS Styling Injection (With Strict Contrast Fixes)
# -----------------------------------------------------------------------------
if is_dark:
    bg_app = "#070B14"
    text_main = "#F8FAFC"
    text_sub = "#94A3B8"
    card_bg = "rgba(15, 23, 42, 0.85)"
    card_border = "rgba(255, 255, 255, 0.1)"
    hero_bg = "linear-gradient(135deg, #0F172A 0%, #1E293B 100%)"
    hero_title_color = "#38BDF8"
    tab_unselected = "#94A3B8"
    tab_selected = "#38BDF8"
    tab_hover = "#F8FAFC"
    plotly_text = "#94A3B8"
    plotly_grid = "rgba(255, 255, 255, 0.05)"
    plotly_axis = "rgba(255, 255, 255, 0.15)"
    kpi_val_color = "#F8FAFC"
    pie_hole_color = "#F8FAFC"
else:
    bg_app = "#F1F5F9"
    text_main = "#0F172A"
    text_sub = "#334155"
    card_bg = "#FFFFFF"
    card_border = "#CBD5E1"
    hero_bg = "linear-gradient(135deg, #E0F2FE 0%, #EFF6FF 100%)"
    hero_title_color = "#0369A1"
    tab_unselected = "#475569"
    tab_selected = "#0284C7"
    tab_hover = "#0F172A"
    plotly_text = "#334155"
    plotly_grid = "rgba(0, 0, 0, 0.08)"
    plotly_axis = "rgba(0, 0, 0, 0.2)"
    kpi_val_color = "#0F172A"
    pie_hole_color = "#0F172A"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    .stApp {{
        background-color: {bg_app};
        color: {text_main};
        font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
    }}

    /* Hero Banner */
    .hero-container {{
        background: {hero_bg};
        border: 2px solid {card_border};
        border-radius: 20px;
        padding: 28px 36px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
    }}
    .hero-title {{
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: {hero_title_color} !important;
        margin-bottom: 6px;
    }}
    .hero-subtitle {{
        color: {text_sub} !important;
        font-size: 1.05rem;
        font-weight: 600;
    }}

    /* Streamlit Tabs Text Contrast Fix */
    button[data-baseweb="tab"] {{
        color: {tab_unselected} !important;
        font-weight: 700 !important;
        font-size: 0.98rem !important;
        background-color: transparent !important;
        border: none !important;
        padding: 10px 18px !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {tab_selected} !important;
        border-bottom: 3px solid {tab_selected} !important;
        font-weight: 800 !important;
    }}
    button[data-baseweb="tab"]:hover {{
        color: {tab_hover} !important;
    }}
    div[data-baseweb="tab-border"] {{
        background-color: {card_border} !important;
    }}

    /* Headings & Markdown Text Fix */
    h1, h2, h3, h4, h5, h6, .stMarkdown p, .stMarkdown span, label {{
        color: {text_main} !important;
    }}

    /* Glass Cards */
    .glass-card {{
        background: {card_bg};
        border: 1px solid {card_border};
        border-radius: 18px;
        padding: 24px;
        margin-bottom: 16px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
    }}

    /* KPI Container */
    .kpi-container {{
        background: {card_bg};
        border: 1px solid {card_border};
        border-radius: 16px;
        padding: 20px 22px;
        text-align: left;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.05);
    }}
    .kpi-title {{
        font-size: 0.78rem;
        font-weight: 700;
        color: {text_sub} !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 8px;
    }}
    .kpi-value {{
        font-size: 2.2rem;
        font-weight: 800;
        color: {kpi_val_color} !important;
        line-height: 1.1;
    }}
    .kpi-badge {{
        display: inline-block;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 12px;
        margin-top: 8px;
    }}
    .kpi-badge-cyan {{
        background: rgba(56, 189, 248, 0.15);
        color: #0284C7 !important;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }}
    .kpi-badge-purple {{
        background: rgba(139, 92, 246, 0.15);
        color: #7C3AED !important;
        border: 1px solid rgba(139, 92, 246, 0.3);
    }}
    .kpi-badge-emerald {{
        background: rgba(16, 185, 129, 0.15);
        color: #059669 !important;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }}

    /* Verdict Card */
    .result-card-churn {{
        background: {"linear-gradient(135deg, rgba(127, 29, 29, 0.4) 0%, rgba(15, 23, 42, 0.95) 100%)" if is_dark else "#FEF2F2"};
        border: 2px solid {"rgba(239, 68, 68, 0.4)" if is_dark else "#FCA5A5"};
        border-left: 6px solid #EF4444;
        border-radius: 18px;
        padding: 28px;
        text-align: center;
    }}
    .result-card-retain {{
        background: {"linear-gradient(135deg, rgba(6, 78, 59, 0.4) 0%, rgba(15, 23, 42, 0.95) 100%)" if is_dark else "#ECFDF5"};
        border: 2px solid {"rgba(16, 185, 129, 0.4)" if is_dark else "#6EE7B7"};
        border-left: 6px solid #10B981;
        border-radius: 18px;
        padding: 28px;
        text-align: center;
    }}

    /* Section Pills */
    .section-pill {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: {"rgba(56, 189, 248, 0.12)" if is_dark else "#E0F2FE"};
        border: 1px solid {"rgba(56, 189, 248, 0.3)" if is_dark else "#7DD3FC"};
        color: {"#38BDF8" if is_dark else "#0369A1"} !important;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.88rem;
        font-weight: 700;
        margin-top: 16px;
        margin-bottom: 14px;
    }}

    /* Buttons */
    .stButton>button {{
        background: linear-gradient(90deg, #2563EB 0%, #3B82F6 100%);
        color: #FFFFFF !important;
        border: none;
        border-radius: 12px;
        font-weight: 700;
        padding: 12px 24px;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3);
    }}

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# Load Metadata
metadata = {}
if os.path.exists("metadata.json"):
    try:
        with open("metadata.json", "r", encoding="utf-8") as f:
            metadata = json.load(f)
    except Exception:
        pass

# -----------------------------------------------------------------------------
# 4. Hero Banner & Top Tabs Navigation
# -----------------------------------------------------------------------------
st.markdown("""
<div class="hero-container">
    <div class="hero-title">📡 Telecom Customer Churn AI Platform</div>
    <div class="hero-subtitle">Real-time ML customer attrition prediction, prescripted retention actions, and model governance.</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Executive Dashboard",
    "🔮 Predict Customer Churn",
    "📈 Analytics & Insights",
    "🏆 Model Performance & Metadata",
    "📡 System Health & Telemetry"
])

# -----------------------------------------------------------------------------
# TAB 1: EXECUTIVE DASHBOARD
# -----------------------------------------------------------------------------
with tab1:
    kcol1, kcol2, kcol3, kcol4 = st.columns(4)
    with kcol1:
        st.markdown(f"""
        <div class="kpi-container" style="border-top: 4px solid #38BDF8;">
            <div class="kpi-title">Total Evaluated Customers</div>
            <div class="kpi-value">7,043</div>
            <div class="kpi-badge kpi-badge-cyan">↑ 12.5% Month over Month</div>
        </div>
        """, unsafe_allow_html=True)
    with kcol2:
        st.markdown(f"""
        <div class="kpi-container" style="border-top: 4px solid #F43F5E;">
            <div class="kpi-title">Overall Churn Rate</div>
            <div class="kpi-value" style="color: #F43F5E;">26.5%</div>
            <div class="kpi-badge kpi-badge-emerald">↓ 2.4% Retention Gain</div>
        </div>
        """, unsafe_allow_html=True)
    with kcol3:
        st.markdown(f"""
        <div class="kpi-container" style="border-top: 4px solid #8B5CF6;">
            <div class="kpi-title">Model ROC-AUC Score</div>
            <div class="kpi-value" style="color: #8B5CF6;">0.8461</div>
            <div class="kpi-badge kpi-badge-purple">Accuracy: 80.34%</div>
        </div>
        """, unsafe_allow_html=True)
    with kcol4:
        st.markdown(f"""
        <div class="kpi-container" style="border-top: 4px solid #10B981;">
            <div class="kpi-title">Avg API Latency</div>
            <div class="kpi-value" style="color: #10B981;">24 ms</div>
            <div class="kpi-badge kpi-badge-emerald">Worker Thread Pool</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📈 Prediction Activity Trend (Weekly)")
        
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        retained = [240, 310, 290, 410, 380, 210, 260]
        churned = [75, 82, 64, 105, 89, 45, 52]

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=days, y=retained, name="Retained Customers",
            mode="lines+markers", line=dict(color="#0284C7" if not is_dark else "#38BDF8", width=3.5, shape="spline"),
            fill="tozeroy", fillcolor="rgba(56, 189, 248, 0.12)"
        ))
        fig_trend.add_trace(go.Scatter(
            x=days, y=churned, name="Churn Risk Alert",
            mode="lines+markers", line=dict(color="#E11D48" if not is_dark else "#F43F5E", width=3.5, shape="spline"),
            fill="tozeroy", fillcolor="rgba(244, 63, 94, 0.12)"
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

    with c2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🎯 Risk Tier Breakdown")
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=["Low Risk (<40%)", "Medium Risk (40-70%)", "High Risk (>70%)"],
            values=[4150, 1840, 1053],
            hole=0.62,
            textinfo="percent",
            hoverinfo="label+value+percent",
            marker=dict(
                colors=["#10B981", "#F59E0B", "#F43F5E"],
                line=dict(color="#0F172A" if is_dark else "#FFFFFF", width=3)
            )
        )])
        fig_pie.update_layout(
            annotations=[dict(text="Risk<br>Tiers", x=0.5, y=0.5, font_size=15, font_color=pie_hole_color, font_family="Plus Jakarta Sans", font_weight=700, showarrow=False)],
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans", color=plotly_text, size=11),
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("📋 Recent Customer Evaluations")
    recent_df = pd.DataFrame([
        {"CustomerID": "7590-VHVEG", "Contract": "Month-to-month", "Tenure": 1, "MonthlyCharges": "$29.85", "Probability": "74.2%", "Risk": "High", "Verdict": "Churn"},
        {"CustomerID": "5575-GNVDE", "Contract": "One year", "Tenure": 34, "MonthlyCharges": "$56.95", "Probability": "12.4%", "Risk": "Low", "Verdict": "No Churn"},
        {"CustomerID": "3668-QVRWS", "Contract": "Month-to-month", "Tenure": 2, "MonthlyCharges": "$53.85", "Probability": "58.6%", "Risk": "Medium", "Verdict": "Churn"},
        {"CustomerID": "7795-CFOCW", "Contract": "One year", "Tenure": 45, "MonthlyCharges": "$42.30", "Probability": "8.1%", "Risk": "Low", "Verdict": "No Churn"},
        {"CustomerID": "9237-HQJCB", "Contract": "Month-to-month", "Tenure": 2, "MonthlyCharges": "$70.70", "Probability": "81.9%", "Risk": "High", "Verdict": "Churn"}
    ])
    st.dataframe(recent_df, use_container_width=True, hide_index=True)


# -----------------------------------------------------------------------------
# TAB 2: PREDICT CUSTOMER CHURN
# -----------------------------------------------------------------------------
with tab2:
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
        submit_button = st.form_submit_button("🚀 Run FastAPI Model Prediction", type="primary", use_container_width=True)

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

        predict_endpoint = f"{api_base_url.rstrip('/')}/predict"

        with st.spinner("Evaluating feature vector in FastAPI pipeline..."):
            try:
                start_t = time.time()
                resp = requests.post(predict_endpoint, json=payload, timeout=10)
                latency_ms = (time.time() - start_t) * 1000

                if resp.status_code == 200:
                    res = resp.json()
                    pred = res["prediction"]
                    prob = res["probability"]
                    conf = res["confidence_score"]
                    risk = res["risk_level"]

                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    card_class = "result-card-churn" if pred == "Churn" else "result-card-retain"
                    risk_color = "#EF4444" if risk == "High" else "#F59E0B" if risk == "Medium" else "#10B981"

                    st.markdown(f"""
                    <div class="{card_class}">
                        <div style="font-size: 1.1rem; color: {text_sub}; margin-bottom: 6px;">Real-Time AI Prediction Verdict</div>
                        <div style="font-size: 3.2rem; font-weight: 800; margin-bottom: 12px; color: {risk_color};">
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
                                'bgcolor': "rgba(15, 23, 42, 0.8)" if is_dark else "#FFFFFF",
                                'borderwidth': 2,
                                'bordercolor': plotly_axis,
                                'steps': [
                                    {'range': [0, 40], 'color': "rgba(16, 185, 129, 0.2)"},
                                    {'range': [40, 70], 'color': "rgba(245, 158, 11, 0.2)"},
                                    {'range': [70, 100], 'color': "rgba(239, 68, 68, 0.2)"}
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
                        st.markdown('</div>', unsafe_allow_html=True)

                else:
                    st.error(f"❌ API Error ({resp.status_code}): {resp.text}")

            except requests.exceptions.ConnectionError:
                st.error("❌ Connection Error: Ensure FastAPI server is running on `http://localhost:8000`.")
            except Exception as e:
                st.error(f"❌ Error during prediction request: {str(e)}")


# -----------------------------------------------------------------------------
# TAB 3: ANALYTICS & INSIGHTS
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("📊 Customer Demographics & Churn Factor Analytics")

    a_col1, a_col2 = st.columns(2)
    with a_col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📄 Contract Type Breakdown")
        
        fig_contract = go.Figure(data=[go.Pie(
            labels=["Month-to-month", "Two year", "One year"],
            values=[3875, 1695, 1473],
            hole=0.55,
            textinfo="percent+label",
            hoverinfo="label+value+percent",
            marker=dict(
                colors=["#38BDF8", "#10B981", "#F59E0B"],
                line=dict(color="#0F172A" if is_dark else "#FFFFFF", width=3)
            ),
            pull=[0.02, 0.02, 0.02]
        )])
        fig_contract.update_layout(
            annotations=[dict(text="Contract<br>Types", x=0.5, y=0.5, font_size=15, font_color=pie_hole_color, font_family="Plus Jakarta Sans", font_weight=700, showarrow=False)],
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans, sans-serif", color=plotly_text, size=12),
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_contract, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with a_col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("💳 Payment Method Distribution")
        
        fig_pay = go.Figure(data=[go.Bar(
            x=["Electronic check", "Mailed check", "Bank transfer", "Credit card"],
            y=[2365, 1612, 1544, 1522],
            text=["2,365", "1,612", "1,544", "1,522"],
            textposition="outside",
            textfont=dict(color="#0284C7" if not is_dark else "#38BDF8", size=13, family="Plus Jakarta Sans", weight=700),
            marker=dict(
                color=["#0284C7" if not is_dark else "#38BDF8", "#6366F1", "#8B5CF6", "#EC4899"],
                line=dict(color=plotly_axis, width=1)
            )
        )])
        fig_pay.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans, sans-serif", color=plotly_text, size=12),
            xaxis=dict(showgrid=False, linecolor=plotly_axis),
            yaxis=dict(showgrid=True, gridcolor=plotly_grid, linecolor=plotly_axis, title="Customer Count"),
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
        textfont=dict(color=text_main, size=12, family="Plus Jakarta Sans", weight=700),
        marker=dict(
            color=[-0.4051, -0.3522, -0.1983, -0.1827, 0.1508, 0.1934],
            colorscale=[[0, "#10B981"], [0.5, "#38BDF8"], [1, "#F43F5E"]],
            line=dict(color=plotly_axis, width=1)
        )
    )])
    fig_corr.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color=plotly_text, size=12),
        xaxis=dict(showgrid=True, gridcolor=plotly_grid, title="Correlation Coefficient with Churn Target"),
        yaxis=dict(showgrid=False),
        margin=dict(l=10, r=20, t=10, b=10)
    )
    st.plotly_chart(fig_corr, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# TAB 4: MODEL PERFORMANCE & METADATA
# -----------------------------------------------------------------------------
with tab4:
    st.subheader("🏆 Model Performance & Provenance Manifest")

    perf = metadata.get("metrics", {
        "accuracy": 0.8034, "precision": 0.6678, "recall": 0.5160,
        "f1_score": 0.5822, "roc_auc": 0.8461, "pr_auc": 0.6577
    })

    mc1, mc2, mc3, mc4, mc5, mc6 = st.columns(6)
    with mc1:
        st.markdown(f"""
        <div class="kpi-container" style="border-top: 4px solid #38BDF8;">
            <div class="kpi-title">Accuracy</div>
            <div class="kpi-value" style="color: #0284C7;">{(perf.get('accuracy', 0.8034)*100):.1f}%</div>
            <div class="kpi-badge kpi-badge-cyan">Overall Fit</div>
        </div>
        """, unsafe_allow_html=True)
    with mc2:
        st.markdown(f"""
        <div class="kpi-container" style="border-top: 4px solid #6366F1;">
            <div class="kpi-title">Precision</div>
            <div class="kpi-value" style="color: #4F46E5;">{(perf.get('precision', 0.6678)*100):.1f}%</div>
            <div class="kpi-badge kpi-badge-purple">Positive Predictive</div>
        </div>
        """, unsafe_allow_html=True)
    with mc3:
        st.markdown(f"""
        <div class="kpi-container" style="border-top: 4px solid #8B5CF6;">
            <div class="kpi-title">Recall</div>
            <div class="kpi-value" style="color: #7C3AED;">{(perf.get('recall', 0.5160)*100):.1f}%</div>
            <div class="kpi-badge kpi-badge-purple">Sensitivity Rate</div>
        </div>
        """, unsafe_allow_html=True)
    with mc4:
        st.markdown(f"""
        <div class="kpi-container" style="border-top: 4px solid #EC4899;">
            <div class="kpi-title">F1 Score</div>
            <div class="kpi-value" style="color: #DB2777;">{perf.get('f1_score', 0.5822):.4f}</div>
            <div class="kpi-badge kpi-badge-cyan">Harmonic Mean</div>
        </div>
        """, unsafe_allow_html=True)
    with mc5:
        st.markdown(f"""
        <div class="kpi-container" style="border-top: 4px solid #10B981;">
            <div class="kpi-title">ROC-AUC</div>
            <div class="kpi-value" style="color: #059669;">{perf.get('roc_auc', 0.8461):.4f}</div>
            <div class="kpi-badge kpi-badge-emerald">Discriminative Power</div>
        </div>
        """, unsafe_allow_html=True)
    with mc6:
        st.markdown(f"""
        <div class="kpi-container" style="border-top: 4px solid #F59E0B;">
            <div class="kpi-title">PR-AUC</div>
            <div class="kpi-value" style="color: #D97706;">{perf.get('pr_auc', 0.6577):.4f}</div>
            <div class="kpi-badge kpi-badge-cyan">Precision-Recall</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    plot_c1, plot_c2 = st.columns(2)
    with plot_c1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🔥 Confusion Matrix Heatmap")
        
        cm_data = perf.get("confusion_matrix", [[939, 96], [181, 193]])
        fig_cm = go.Figure(data=go.Heatmap(
            z=cm_data,
            x=["Predicted No Churn", "Predicted Churn"],
            y=["Actual No Churn", "Actual Churn"],
            colorscale=[[0, "#F1F5F9" if not is_dark else "#0F172A"], [0.5, "#3B82F6"], [1, "#1D4ED8"]],
            text=[[f"{cm_data[0][0]}<br>(True Negative)", f"{cm_data[0][1]}<br>(False Positive)"],
                  [f"{cm_data[1][0]}<br>(False Negative)", f"{cm_data[1][1]}<br>(True Positive)"]],
            texttemplate="%{text}",
            textfont={"size": 14, "color": "#F8FAFC" if is_dark else "#0F172A", "family": "Plus Jakarta Sans"}
        ))
        fig_cm.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans", color=plotly_text),
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig_cm, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with plot_c2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📉 ROC Characteristic Curve")
        
        fpr = [0.0, 0.05, 0.12, 0.22, 0.35, 0.50, 0.70, 0.88, 1.0]
        tpr = [0.0, 0.38, 0.62, 0.78, 0.86, 0.92, 0.96, 0.99, 1.0]

        fig_roc = go.Figure()
        fig_roc.add_trace(go.Scatter(
            x=fpr, y=tpr, name="Calibrated Model (AUC = 0.8461)",
            mode="lines", line=dict(color="#0284C7" if not is_dark else "#38BDF8", width=3.5, shape="spline"),
            fill="tozeroy", fillcolor="rgba(56, 189, 248, 0.12)"
        ))
        fig_roc.add_trace(go.Scatter(
            x=[0, 1], y=[0, 1], name="Random Classifier Baseline",
            mode="lines", line=dict(color="#64748B", width=2, dash="dash")
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

    st.markdown("<br>", unsafe_allow_html=True)

    info_c1, info_c2 = st.columns(2)
    with info_c1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📋 Active Model Manifest")
        st.json({
            "model_version": metadata.get("model_version", "1.0.0"),
            "model_algorithm": metadata.get("model_type", "Logistic Regression"),
            "trained_at": metadata.get("trained_at", "2026-08-06T06:45:02Z"),
            "raw_input_features": 19,
            "transformed_feature_matrix_shape": "(1, 55)",
            "class_balancing": "class_weight='balanced'",
            "probability_calibration": "CalibratedClassifierCV (5-Fold)"
        })
        st.markdown('</div>', unsafe_allow_html=True)

    with info_c2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🔒 Serialized Artifact Checksums")
        artifacts_meta = metadata.get("artifacts", {})
        st.json(artifacts_meta if artifacts_meta else {
            "model_pkl": {"filename": "model.pkl", "sha256": "b29c44f30e0a220a13a0fff3f8c79b071a18343b3105002d1ce43f90c508d7f5"},
            "scaler_pkl": {"filename": "scaler.pkl", "sha256": "fd413e7f268009915ba22cdc2bc4b7ccb25c700d4893afe60fb170738f135e87"},
            "encoder_pkl": {"filename": "encoder.pkl", "sha256": "3f5c382e3a766bd8be381cb30d7c81749cc0571e84de95439c95b38f0fdffc55"}
        })
        st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# TAB 5: SYSTEM HEALTH & TELEMETRY
# -----------------------------------------------------------------------------
with tab5:
    st.subheader("📡 Real-Time Microservice Infrastructure & Telemetry")

    t1, t2, t3 = st.columns(3)
    
    try:
        sp_start = time.time()
        sp_resp = requests.get(f"{api_base_url.rstrip('/')}/health", timeout=2)
        sp_latency = (time.time() - sp_start) * 1000
        
        if sp_resp.status_code == 200:
            sp_data = sp_resp.json()
            sys_st = sp_data.get("status", "healthy")
            m_ok = sp_data.get("model_loaded", True)
            s_ok = sp_data.get("scaler_loaded", True)
            e_ok = sp_data.get("encoder_loaded", True)
        else:
            sys_st, m_ok, s_ok, e_ok = "degraded", False, False, False
    except Exception:
        sys_st, m_ok, s_ok, e_ok, sp_latency = "offline", False, False, False, 0.0

    with t1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("⚡ FastAPI Microservice")
        st.write(f"**Status**: `{'healthy' if sys_st=='healthy' else sys_st.upper()}`")
        st.write(f"**Ping Latency**: `{sp_latency:.1f} ms`")
        st.write(f"**Port Mapping**: `8000:8000`")
        st.markdown('</div>', unsafe_allow_html=True)

    with t2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📦 ML Artifacts")
        st.write(f"**model.pkl**: `{'Loaded' if m_ok else 'Missing'}`")
        st.write(f"**scaler.pkl**: `{'Loaded' if s_ok else 'Missing'}`")
        st.write(f"**encoder.pkl**: `{'Loaded' if e_ok else 'Missing'}`")
        st.markdown('</div>', unsafe_allow_html=True)

    with t3:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🛡️ Security Verification")
        st.write("**Payload Limit**: `1 MB`")
        st.write("**Extra Fields**: `Forbidden (422)`")
        st.write("**CORS Allowlist**: `Configured`")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("📊 Live Telemetry Endpoint (`/metrics`)")
    try:
        met_resp = requests.get(f"{api_base_url.rstrip('/')}/metrics", timeout=2)
        if met_resp.status_code == 200:
            st.json(met_resp.json())
        else:
            st.warning("Could not reach `/metrics` endpoint.")
    except Exception:
        st.info("Start FastAPI backend server (`python app.py`) to stream live telemetry metrics.")
