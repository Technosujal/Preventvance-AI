import streamlit as st
import api_client
import utils
import pandas as pd
from datetime import datetime, timedelta
from theme import apply_light_theme, create_navbar, create_metric_card

st.set_page_config(
    page_title="Patient Dashboard", 
    layout="wide",
    page_icon="👤"
)

# --- Authentication Check ---
if "token" not in st.session_state or st.session_state.get("user_role") != "patient":
    st.warning("⚠️ Please log in to access your dashboard.")
    if st.button("Go to Login"):
        st.switch_page("app.py")
    st.stop()

# --- Layout & Data Loading ---
apply_light_theme()

user_name = st.session_state.get("user_name", "Patient")
user_role = st.session_state.get("user_role", "Patient")
patient_id = st.session_state.get("user_id")

# Fetch Data
with st.spinner("Loading health data..."):
    patient_data = api_client.get_patient_details(patient_id)
    risk_data = api_client.get_latest_prediction(patient_id)
    recommendations = api_client.get_recommendations(patient_id)
    appointments_list = api_client.get_my_consultations()

if not patient_data:
    st.error("⚠️ Failed to load patient data.")
    st.stop()

# Background Overlay
import os
import base64
try:
    img_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "patient_bg.png")
    if os.path.exists(img_path):
        st.markdown("""
            <div class="bg-overlay" style="background-image: url('data:image/png;base64,%s'); opacity: 0.15;"></div>
        """ % base64.b64encode(open(img_path, "rb").read()).decode(), unsafe_allow_html=True)
except:
    pass

create_navbar(user_name, user_role)

# --- Header Section ---
st.markdown("""
<div class="animate-fade-in no-print">
    <div style="background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark)); 
                color: white; padding: 2.5rem; border-radius: var(--border-radius-xl); 
                margin-bottom: 2rem; box-shadow: var(--shadow-xl); position: relative; overflow: hidden;">
        <div style="position: absolute; top: -30px; right: -30px; font-size: 10rem; opacity: 0.1; transform: rotate(15deg);">👤</div>
        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 800; color: white; letter-spacing: -0.04em;">My Health Portal</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9; font-weight: 500;">
            Welcome back, <b>%s</b>. Track your wellness and manage appointments.
        </p>
    </div>
</div>
""" % user_name, unsafe_allow_html=True)

# --- Tabs ---
tabs = st.tabs(["📊 Overview", "🩺 Health Checkup", "🤖 AI Assistant", "📈 Risk Analysis"])

# --- TAB 1: OVERVIEW ---
with tabs[0]:
    col1, col2, col3 = st.columns(3)
    with col1:
        create_metric_card("Age", f"{patient_data.get('age', 'N/A')} yrs", "🎂")
    with col2:
        create_metric_card("BMI", f"{patient_data.get('bmi', 0):.1f}", "⚖️")
    with col3:
         # ABHA ID as a metric
        create_metric_card("ABHA ID", patient_data.get('abha_id', 'N/A'), "🆔")
    
    st.divider()

    # --- PDF Report Download ---
    col_pdf, _ = st.columns([1, 2])
    with col_pdf:
        if st.button("📄 Download Full Health Report", use_container_width=True):
            with st.spinner("Generating your report..."):
                pdf_content = api_client.get_pdf_report(patient_id, ["Overview", "Diabetes", "Liver", "Heart", "Mental Health"])
                if pdf_content:
                    st.success("✅ Report Ready!")
                    st.download_button(
                        label="⬇️ Click to Download",
                        data=pdf_content,
                        file_name=f"My_Health_Report_{patient_data.get('abha_id')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    st.error("❌ Failed to generate report. Please try again later.")
    
    st.divider()
    
    # Disease Risk Summary
    st.subheader("Current Risk Status")
    if risk_data:
        utils.display_risk_assessment(risk_data)
    else:
        st.info("No assessment data available. Visit the 'Health Checkup' tab to begin.")
    
    st.divider()
    
    # Recommendations Summary
    col_recs, col_meds = st.columns(2)
    with col_recs:
        st.subheader("💡 Wellness Tips")
        if recommendations and any(recommendations.values()):
            # Show top 3 recommendations
            all_recs = []
            for cat, rec_list in recommendations.items():
                for r in rec_list:
                    all_recs.append(r)
            
            for rec in all_recs[:3]:
                st.info(f"**{rec.get('category', 'Tip')}:** {rec.get('recommendation_text')}")
        else:
            st.success("You're doing great! Keep maintaining your healthy habits.")

# --- TAB 2: HEALTH CHECKUP ---
with tabs[1]:
    st.subheader("Comprehensive Diagnostic Wizard")
    st.write("Complete these 4 quick assessments for a full health profile.")
    
    # Progress bar and status
    completed = []
    if patient_data.get('diabetes_assessments'): completed.append("Diabetes")
    if patient_data.get('heart_assessments'): completed.append("Heart")
    if patient_data.get('liver_assessments'): completed.append("Liver")
    if patient_data.get('mental_health_assessments'): completed.append("Mental Health")
    
    st.progress(len(completed) / 4)
    st.write(f"Progress: {len(completed) or 0}/4 Assessments Completed")
    
    wizard_step = st.radio("Choose assessment to start/update:", 
                          ["Diabetes", "Heart", "Liver", "Mental Health"], horizontal=True)
    
    # Assessment forms (Simplified for the wizard)
    if wizard_step == "Diabetes":
        with st.form("diabetes_form"):
            col1, col2 = st.columns(2)
            glucose = col1.number_input("Glucose Level (mg/dL)", 0.0, 500.0, 100.0)
            bp = col2.number_input("Blood Pressure (mm Hg)", 0.0, 250.0, 80.0)
            insulin = col1.number_input("Insulin Level (mu U/ml)", 0.0, 1000.0, 30.0)
            skin = col2.number_input("Skin Thickness (mm)", 0.0, 100.0, 20.0)
            
            is_pregnant = st.checkbox("Is Pregnant?", value=False)
            has_history = st.checkbox("Family History of Diabetes?", value=False)
            
            if st.form_submit_button("Save Diabetes Data"):
                res = api_client.add_assessment(patient_id, "diabetes", {
                    "pregnancy": is_pregnant,
                    "glucose": glucose, 
                    "blood_pressure": bp, 
                    "skin_thickness": skin,
                    "insulin": insulin, 
                    "diabetes_history": has_history
                })
                if res: st.success("Diabetes data saved!")
    
    elif wizard_step == "Heart":
        with st.form("heart_form"):
            st.write("Vitals & Labs")
            col_h1, col_h2 = st.columns(2)
            sys_bp = col_h1.number_input("Systolic BP", 50, 250, 120)
            dia_bp = col_h2.number_input("Diastolic BP", 30, 150, 80)
            chol = col_h1.number_input("Total Cholesterol", 100.0, 500.0, 200.0)
            tg = col_h2.number_input("Triglycerides", 50.0, 500.0, 150.0)
            ldl = col_h1.number_input("LDL Cholesterol", 20.0, 300.0, 100.0)
            hdl = col_h2.number_input("HDL Cholesterol", 10.0, 150.0, 50.0)
            
            st.write("Lifestyle & History")
            col_b1, col_b2, col_b3 = st.columns(3)
            has_dm = col_b1.checkbox("Diabetes?")
            has_ht = col_b2.checkbox("Hypertension?")
            is_obese = col_b3.checkbox("Obesity?")
            is_smoker = col_b1.checkbox("Smoker?")
            is_alc = col_b2.checkbox("Alcohol Consumption?")
            is_active = col_b3.checkbox("Physical Activity?")
            has_fam = col_b1.checkbox("Family History?")
            has_ha = col_b2.checkbox("Heart Attack History?")
            
            col_s1, col_s2 = st.columns(2)
            diet = col_s1.slider("Diet Score (1-10)", 1, 10, 5)
            stress = col_s2.slider("Stress Level (1-10)", 1, 10, 5)
            poll = col_s1.number_input("Air Pollution Exposure", 0.0, 100.0, 20.0)
            
            if st.form_submit_button("Save Heart Data"):
                res = api_client.add_assessment(patient_id, "heart", {
                    "diabetes": has_dm,
                    "hypertension": has_ht,
                    "obesity": is_obese,
                    "smoking": is_smoker,
                    "alcohol_consumption": is_alc,
                    "physical_activity": is_active,
                    "diet_score": diet,
                    "cholesterol_level": chol,
                    "triglyceride_level": tg,
                    "ldl_level": ldl,
                    "hdl_level": hdl,
                    "systolic_bp": sys_bp,
                    "diastolic_bp": dia_bp,
                    "air_pollution_exposure": poll,
                    "family_history": has_fam,
                    "stress_level": stress,
                    "heart_attack_history": has_ha
                })
                if res: st.success("Heart data saved!")

    elif wizard_step == "Liver":
        with st.form("liver_form"):
            st.write("Liver function markers")
            col_l1, col_l2 = st.columns(2)
            t_bil = col_l1.number_input("Total Bilirubin", 0.1, 15.0, 1.0)
            d_bil = col_l2.number_input("Direct Bilirubin", 0.1, 10.0, 0.3)
            alk = col_l1.number_input("Alkaline Phosphatase", 50.0, 1000.0, 100.0)
            sgpt = col_l2.number_input("SGPT/ALT", 5.0, 500.0, 40.0)
            sgot = col_l1.number_input("SGOT/AST", 5.0, 500.0, 40.0)
            t_prot = col_l2.number_input("Total Protein", 1.0, 15.0, 7.0)
            alb = col_l1.number_input("Albumin", 1.0, 10.0, 4.0)
            
            if st.form_submit_button("Save Liver Data"):
                res = api_client.add_assessment(patient_id, "liver", {
                    "total_bilirubin": t_bil,
                    "direct_bilirubin": d_bil,
                    "alkaline_phosphatase": alk,
                    "sgpt_alamine_aminotransferase": sgpt,
                    "sgot_aspartate_aminotransferase": sgot,
                    "total_protein": t_prot,
                    "albumin": alb
                })
                if res: st.success("Liver data saved!")

    elif wizard_step == "Mental Health":
        with st.form("mental_form"):
            st.write("Clinical Screening")
            col_m1, col_m2 = st.columns(2)
            phq = col_m1.number_input("PHQ-9 Score", 0, 27, 5)
            gad = col_m2.number_input("GAD-7 Score", 0, 21, 5)
            
            st.write("Symptoms")
            s_col1, s_col2 = st.columns(2)
            dep = s_col1.checkbox("Depressiveness")
            sui = s_col2.checkbox("Suicidal Ideation")
            anx = s_col1.checkbox("Anxiousness")
            slp = s_col2.checkbox("Sleepiness/Insomnia")
            
            if st.form_submit_button("Save Mental Health Data"):
                res = api_client.add_assessment(patient_id, "mental_health", {
                    "phq_score": phq,
                    "gad_score": gad,
                    "depressiveness": dep,
                    "suicidal": sui,
                    "anxiousness": anx,
                    "sleepiness": slp
                })
                if res: st.success("Mental health data saved!")

    st.caption("Note: Ensure you enter accurate clinical data for a precise risk profile.")

# --- TAB 3: AI ASSISTANT ---
with tabs[2]:
    st.subheader("💬 PreventVance AI Chatbot")
    st.write("Ask me about your risks, lifestyle tips, or platform orientation.")
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display Chat History
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("How can I help you today?"):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("AI is thinking..."):
                response = api_client.send_chat_message(prompt, st.session_state.chat_history)
                st.markdown(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})

# --- TAB 4: RISK ANALYSIS ---
with tabs[3]:
    st.subheader("📊 Detailed Health Risk Breakdown")
    if risk_data:
        disease_focus = st.multiselect("Select Disease Focus", ["Diabetes", "Heart", "Liver", "Mental Health"], default=["Diabetes"])
        for d in disease_focus:
            st.markdown(f"#### {d} Analysis")
            utils.display_risk_level_details(d.lower().replace(" ", "_"), risk_data)
    else:
        st.info("Complete assessments to see your risk analysis.")