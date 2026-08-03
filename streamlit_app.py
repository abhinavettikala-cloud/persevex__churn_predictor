import streamlit as st
import requests
import json
import time
import os

# -----------------------------------------------------------------------------
# 1. Page Configuration & Custom CSS Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Telecom Churn Predictor AI",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Custom CSS for Premium Design & Visual Excellence
st.markdown("""
<style>
    /* Global Styles */
    .main {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    
    /* Header Styling */
    .header-container {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    .header-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38BDF8 0%, #818CF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }
    .header-subtitle {
        color: #94A3B8;
        font-size: 1.05rem;
    }
    
    /* Card Styles */
    .metric-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .churn-danger {
        border-left: 6px solid #EF4444 !important;
        background: linear-gradient(135deg, #2A1215 0%, #1E293B 100%);
    }
    .churn-safe {
        border-left: 6px solid #10B981 !important;
        background: linear-gradient(135deg, #06281E 0%, #1E293B 100%);
    }
    
    /* Risk Badges */
    .badge-high {
        background-color: #7F1D1D;
        color: #FCA5A5;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.95rem;
    }
    .badge-medium {
        background-color: #78350F;
        color: #FDE68A;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.95rem;
    }
    .badge-low {
        background-color: #064E3B;
        color: #6EE7B7;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.95rem;
    }
    
    /* Section Divider */
    .section-header {
        color: #38BDF8;
        font-size: 1.2rem;
        font-weight: 600;
        margin-top: 16px;
        margin-bottom: 12px;
        border-bottom: 1px solid #334155;
        padding-bottom: 6px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. Sidebar - Branding, API Configuration & Health Diagnostics
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3059/3059502.png", width=70)
    st.title("Telecom Churn AI")
    st.caption("Production Customer Analytics Engine")
    st.markdown("---")

    # API Base URL Input
    st.subheader("⚙️ API Configuration")
    default_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    api_base_url = st.text_input(
        "FastAPI Backend URL",
        value=default_url,
        help="URL of running FastAPI server endpoint"
    )

    # API Connection Diagnostics
    st.subheader("📡 Backend Status")
    health_url = f"{api_base_url.rstrip('/')}/health"
    
    try:
        health_resp = requests.get(health_url, timeout=3)
        if health_resp.status_code == 200:
            health_data = health_resp.json()
            if health_data.get("status") == "ok":
                st.success("🟢 API Connected (Model Loaded)")
            else:
                st.warning("🟡 API Degrading (Artifacts Unloaded)")
        else:
            st.error(f"🔴 API Offline ({health_resp.status_code})")
    except Exception:
        st.error("🔴 API Connection Failed. Start server with `python -m uvicorn app:app`")

    st.markdown("---")

    # Quick Demo Presets
    st.subheader("🎯 Demo Presets")
    st.caption("Pre-fill form with representative customer profiles:")
    
    preset_choice = st.radio(
        "Select Profile Preset:",
        options=["Default / Manual Input", "⚡ High Risk Churner", "🛡️ Loyal Low-Risk Customer"]
    )

# Set pre-fill form variables based on preset selection
if preset_choice == "⚡ High Risk Churner":
    default_gender = "Female"
    default_senior = 0
    default_partner = "No"
    default_dependents = "No"
    default_tenure = 1
    default_phone = "Yes"
    default_multiple = "No"
    default_internet = "Fiber optic"
    default_security = "No"
    default_backup = "No"
    default_device = "No"
    default_tech = "No"
    default_tv = "No"
    default_movies = "No"
    default_contract = "Month-to-month"
    default_paperless = "Yes"
    default_payment = "Electronic check"
    default_monthly = 85.50
    default_total = 85.50
elif preset_choice == "🛡️ Loyal Low-Risk Customer":
    default_gender = "Male"
    default_senior = 0
    default_partner = "Yes"
    default_dependents = "Yes"
    default_tenure = 65
    default_phone = "Yes"
    default_multiple = "Yes"
    default_internet = "DSL"
    default_security = "Yes"
    default_backup = "Yes"
    default_device = "Yes"
    default_tech = "Yes"
    default_tv = "Yes"
    default_movies = "Yes"
    default_contract = "Two year"
    default_paperless = "No"
    default_payment = "Bank transfer (automatic)"
    default_monthly = 60.00
    default_total = 3900.00
else:
    default_gender = "Female"
    default_senior = 0
    default_partner = "Yes"
    default_dependents = "No"
    default_tenure = 12
    default_phone = "Yes"
    default_multiple = "No"
    default_internet = "Fiber optic"
    default_security = "No"
    default_backup = "Yes"
    default_device = "No"
    default_tech = "No"
    default_tv = "Yes"
    default_movies = "No"
    default_contract = "Month-to-month"
    default_paperless = "Yes"
    default_payment = "Electronic check"
    default_monthly = 70.35
    default_total = 844.20

# -----------------------------------------------------------------------------
# 3. Main Dashboard Header
# -----------------------------------------------------------------------------
st.markdown("""
<div class="header-container">
    <div class="header-title">Telecom Customer Churn Predictor</div>
    <div class="header-subtitle">Predict customer attrition risk using Machine Learning & FastAPI microservices</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. Interactive Customer Input Form
# -----------------------------------------------------------------------------
with st.form("churn_prediction_form"):
    st.markdown('<div class="section-header">👤 1. Customer Demographics</div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        gender = st.selectbox("Gender", options=["Female", "Male"], index=0 if default_gender == "Female" else 1)
    with col2:
        senior_citizen = st.selectbox("Senior Citizen (>=65)", options=[0, 1], format_func=lambda x: "Yes" if x == 1 else "No", index=default_senior)
    with col3:
        partner = st.selectbox("Has Partner", options=["Yes", "No"], index=0 if default_partner == "Yes" else 1)
    with col4:
        dependents = st.selectbox("Has Dependents", options=["Yes", "No"], index=0 if default_dependents == "Yes" else 1)

    st.markdown('<div class="section-header">🌐 2. Network & Connectivity Services</div>', unsafe_allow_html=True)
    col5, col6, col7 = st.columns(3)
    with col5:
        phone_service = st.selectbox("Phone Service", options=["Yes", "No"], index=0 if default_phone == "Yes" else 1)
    with col6:
        multiple_lines = st.selectbox("Multiple Lines", options=["No phone service", "No", "Yes"], index=["No phone service", "No", "Yes"].index(default_multiple))
    with col7:
        internet_service = st.selectbox("Internet Service Provider", options=["Fiber optic", "DSL", "No"], index=["Fiber optic", "DSL", "No"].index(default_internet))

    st.markdown('<div class="section-header">🛡️ 3. Digital Services & Security Add-Ons</div>', unsafe_allow_html=True)
    col8, col9, col10 = st.columns(3)
    with col8:
        online_security = st.selectbox("Online Security", options=["No internet service", "No", "Yes"], index=["No internet service", "No", "Yes"].index(default_security))
        online_backup = st.selectbox("Online Backup", options=["No internet service", "No", "Yes"], index=["No internet service", "No", "Yes"].index(default_backup))
    with col9:
        device_protection = st.selectbox("Device Protection", options=["No internet service", "No", "Yes"], index=["No internet service", "No", "Yes"].index(default_device))
        tech_support = st.selectbox("Tech Support", options=["No internet service", "No", "Yes"], index=["No internet service", "No", "Yes"].index(default_tech))
    with col10:
        streaming_tv = st.selectbox("Streaming TV", options=["No internet service", "No", "Yes"], index=["No internet service", "No", "Yes"].index(default_tv))
        streaming_movies = st.selectbox("Streaming Movies", options=["No internet service", "No", "Yes"], index=["No internet service", "No", "Yes"].index(default_movies))

    st.markdown('<div class="section-header">💳 4. Billing, Charges & Contract Term</div>', unsafe_allow_html=True)
    col11, col12, col13 = st.columns(3)
    with col11:
        tenure = st.number_input("Tenure (Months)", min_value=0, max_value=120, value=default_tenure, step=1)
        contract = st.selectbox("Contract Type", options=["Month-to-month", "One year", "Two year"], index=["Month-to-month", "One year", "Two year"].index(default_contract))
    with col12:
        paperless_billing = st.selectbox("Paperless Billing", options=["Yes", "No"], index=0 if default_paperless == "Yes" else 1)
        payment_method = st.selectbox("Payment Method", options=[
            "Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"
        ], index=[
            "Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"
        ].index(default_payment))
    with col13:
        monthly_charges = st.number_input("Monthly Charges ($)", min_value=0.0, max_value=300.0, value=float(default_monthly), step=1.0)
        total_charges = st.number_input("Total Charges ($)", min_value=0.0, max_value=10000.0, value=float(default_total), step=10.0)

    st.markdown("<br>", unsafe_allow_html=True)
    submit_button = st.form_submit_button("🔍 Predict Churn Risk", type="primary", use_container_width=True)

# -----------------------------------------------------------------------------
# 5. Prediction Execution & REST API Consumption
# -----------------------------------------------------------------------------
if submit_button:
    # Construct REST API JSON Payload
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

    with st.spinner("Connecting to FastAPI backend & evaluating ML model..."):
        time.sleep(0.3)  # Smooth UI transition
        try:
            response = requests.post(predict_endpoint, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                
                prediction = result["prediction"]
                probability = result["probability"]
                confidence = result["confidence_score"]
                risk_level = result["risk_level"]
                timestamp = result["timestamp"]

                st.markdown("### 📈 Prediction Results")
                
                card_class = "churn-danger" if prediction == "Churn" else "churn-safe"
                
                # Assign Risk Badge Class
                if risk_level == "High":
                    badge_html = '<span class="badge-high">⚠️ HIGH RISK</span>'
                elif risk_level == "Medium":
                    badge_html = '<span class="badge-medium">⚡ MEDIUM RISK</span>'
                else:
                    badge_html = '<span class="badge-low">🛡️ LOW RISK</span>'

                # Display Main Prediction Card
                st.markdown(f"""
                <div class="metric-card {card_class}">
                    <div style="font-size: 1.1rem; color: #94A3B8; margin-bottom: 6px;">Customer Churn Classification</div>
                    <div style="font-size: 2.8rem; font-weight: 800; margin-bottom: 10px;">
                        {'🔴 ' + prediction if prediction == 'Churn' else '🟢 ' + prediction}
                    </div>
                    <div>{badge_html}</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Metrics Columns
                res_col1, res_col2, res_col3 = st.columns(3)
                with res_col1:
                    st.metric("Churn Probability", f"{probability * 100:.1f}%")
                with res_col2:
                    st.metric("Model Confidence", f"{confidence * 100:.1f}%")
                with res_col3:
                    st.metric("Risk Assessment", risk_level)

                # Confidence Meter / Progress Bar
                st.markdown("**Churn Probability Progress Gauge:**")
                st.progress(float(probability))

                # Business Recommendations based on Churn Risk
                if prediction == "Churn":
                    st.error(f"⚠️ **High Churn Warning**: This customer has a **{probability*100:.1f}%** probability of canceling service. Recommended Action: Offer 1-Year or 2-Year Contract discounts and complimentary Tech Support.")
                else:
                    st.success(f"✅ **Low Churn Risk**: Customer retention probability is strong (**{(1-probability)*100:.1f}%**). Standard engagement recommended.")

            else:
                st.error(f"❌ API Error ({response.status_code}): {response.text}")

        except requests.exceptions.ConnectionError:
            st.error("❌ Could not connect to FastAPI server. Please verify FastAPI is running on `http://localhost:8000`.")
        except Exception as e:
            st.error(f"❌ An error occurred during prediction request: {str(e)}")
