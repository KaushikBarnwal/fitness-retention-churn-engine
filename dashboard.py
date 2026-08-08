import streamlit as st
import requests

st.set_page_config(page_title="Fitness Churn Engine", page_icon="🏋️", layout="wide")

st.title("Fitness Member Retention & Churn Predictor")
st.write("Input member activity data below to analyze churn probability.")

# Create input form layout
with st.form("churn_form"):
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Member Profile")
        age = st.number_input("Member Age", min_value=12, max_value=100, value=28)
        near_location = st.selectbox("Lives/Works Near Gym Location?", ["No", "Yes"], index=1)
        partner = st.selectbox("Partner Gym Member (Discount via Employer)?", ["No", "Yes"], index=0)
        promo_friends = st.selectbox("Signed up via Friends Promo?", ["No", "Yes"], index=0)
        group_visits = st.selectbox("Participates in Group Classes?", ["No", "Yes"], index=1)
        
    with col2:
        st.subheader("Subscription & Activity")
        contract_period = st.selectbox("Contract Period (Months)", [1, 6, 12], index=1)
        month_to_end_contract = st.number_input("Months Remaining in Contract", min_value=0.0, max_value=12.0, value=6.0)
        lifetime = st.number_input("Member Lifetime (Months)", min_value=0, max_value=120, value=6)
        avg_additional_charges = st.number_input("Avg Monthly Additional Charges (USD)", min_value=0.0, max_value=1000.0, value=50.0)
        avg_freq_total = st.number_input("Avg Visits/Week (Total)", min_value=0.0, max_value=14.0, value=2.0)
        avg_freq_current = st.number_input("Avg Visits/Week (Current Month)", min_value=0.0, max_value=14.0, value=1.8)

    submit_button = st.form_submit_button("Predict Churn Risk")

if submit_button:
    # Match the FastAPI Pydantic model: MemberData
    payload = {
        "Near_Location": 1 if near_location == "Yes" else 0,
        "Partner": 1 if partner == "Yes" else 0,
        "Promo_friends": 1 if promo_friends == "Yes" else 0,
        "Contract_period": contract_period,
        "Group_visits": 1 if group_visits == "Yes" else 0,
        "Age": age,
        "Avg_additional_charges_total": avg_additional_charges,
        "Month_to_end_contract": month_to_end_contract,
        "Lifetime": lifetime,
        "Avg_class_frequency_total": avg_freq_total,
        "Avg_class_frequency_current_month": avg_freq_current
    }
    try:
        # Call the correct FastAPI endpoint
        response = requests.post("http://127.0.0.1:8000/api/predict-churn/", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            churn_risk = result.get("churn_risk", "LOW")
            probability_str = result.get("probability_score", "0.0%")
            recommended_action = result.get("recommended_action", "No Action Needed")
            
            st.divider()
            st.subheader("Prediction Results")
            
            # Display results with metrics and indicators
            col_metric1, col_metric2 = st.columns(2)
            with col_metric1:
                st.metric(label="Churn Risk Level", value=churn_risk)
            with col_metric2:
                st.metric(label="Churn Probability", value=probability_str)
                
            if churn_risk == "HIGH":
                st.error(f"⚠️ **High Churn Risk!**")
                st.info(f"**Recommended Retention Action:** {recommended_action}")
            else:
                st.success(f"✅ **Low Churn Risk**")
                st.write(f"**Recommended Action:** {recommended_action}")
        else:
            st.error(f"API Error {response.status_code}: Check your backend endpoints.")
            st.write(response.text)
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to FastAPI backend. Make sure Uvicorn is running on port 8000!")
