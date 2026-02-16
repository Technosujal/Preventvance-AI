import streamlit as st
import time
import api_client
import utils
import pandas as pd
from datetime import datetime
from theme import apply_light_theme, create_navbar, create_metric_card

st.set_page_config(
    page_title="Admin Dashboard", 
    layout="wide",
    page_icon="👨‍⚕️"
)

# Apply enhanced light theme
apply_light_theme()

utils.check_login(role="admin")

# Create top navigation bar
import os
import base64
try:
    img_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "admin_bg.png")
    if os.path.exists(img_path):
        st.markdown("""
            <div class="bg-overlay" style="background-image: url('data:image/png;base64,%s'); opacity: 0.1;"></div>
        """ % base64.b64encode(open(img_path, "rb").read()).decode(), unsafe_allow_html=True)
except:
    pass

create_navbar(st.session_state.user_name, st.session_state.user_role)

# --- State Management ---
if "admin_view" not in st.session_state:
    st.session_state.admin_view = "main" # main, add_user, view_patients, patient_detail, edit_patient, ai_assistant
if "add_user_step" not in st.session_state:
    st.session_state.add_user_step = 1
if "view_patient_id" not in st.session_state:
    st.session_state.view_patient_id = None

# --- Navigation Callbacks ---
def set_view(view_name):
    st.session_state.admin_view = view_name
    st.rerun()

# --- View: Main Dashboard ---
if st.session_state.admin_view == "main":
    
    st.markdown("""
    <div class="animate-fade-in">
        <div style="background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark)); 
                    color: white; padding: 3rem 2.5rem; border-radius: var(--border-radius-xl); 
                    margin-bottom: 2.5rem; box-shadow: var(--shadow-xl); position: relative; overflow: hidden;">
            <div style="position: absolute; top: -50px; right: -50px; font-size: 15rem; opacity: 0.1; transform: rotate(-15deg);">🩺</div>
            <h1 style="margin: 0; font-size: 3rem; font-weight: 800; color: white; letter-spacing: -0.04em;">Dashboard</h1>
            <p style="margin: 0.75rem 0 0 0; font-size: 1.25rem; opacity: 0.9; font-weight: 500;">
                Welcome back, %s.
            </p>
        </div>
    </div>
    """ % st.session_state.user_name, unsafe_allow_html=True)
    
    # Quick Actions Row
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Register Patient", use_container_width=True, type="primary"):
            set_view("add_user")
    with col2:
        if st.button("👥 Directory", use_container_width=True):
            set_view("view_patients")
    with col3:
        if st.button("🤖 AI Assistant", use_container_width=True):
            set_view("ai_assistant")
    
    st.divider()
    
    # Analytics
    stats = api_client.get_dashboard_stats()
    if stats:
        reg_col1, reg_col2, reg_col3, reg_col4 = st.columns(4)
        create_metric_card("Total Patients", str(stats.get("total_patients", 0)), "Cumulative impact", "success")
        create_metric_card("New Today", str(stats.get("today_registrations", 0)), "Daily target: 10", "primary")
        
        st.subheader("Critical Risk Alerts")
        risk_cols = st.columns(4)
        with risk_cols[0]: create_metric_card("Diabetes", str(stats.get("diabetes_risk_count", 0)), "High Risk", "error")
        with risk_cols[1]: create_metric_card("Liver", str(stats.get("liver_risk_count", 0)), "High Risk", "warning")
        with risk_cols[2]: create_metric_card("Heart", str(stats.get("heart_risk_count", 0)), "High Risk", "error")
        with risk_cols[3]: create_metric_card("Mental Health", str(stats.get("mental_health_risk_count", 0)), "High Risk", "primary")

# --- View: Appointment Manager ---

# --- View: AI Assistant ---
elif st.session_state.admin_view == "ai_assistant":
    st.button("🏠 Back", on_click=set_view, args=("main",))
    st.title("🤖 AI Clinical Assistant")
    
    if "admin_chat_history" not in st.session_state:
        st.session_state.admin_chat_history = []

    for msg in st.session_state.admin_chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about medical guidelines or patient data..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.admin_chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("assistant"):
            response = api_client.send_chat_message(prompt, st.session_state.admin_chat_history)
            st.markdown(response)
        st.session_state.admin_chat_history.append({"role": "assistant", "content": response})

# --- View: Patient Directory ---
elif st.session_state.admin_view == "view_patients":
    st.button("🏠 Back to Dashboard", on_click=set_view, args=("main",))
    st.title("👥 Patient Directory")
    
    # Filters
    col_cat, col_sort, col_search = st.columns([1, 1, 2])
    with col_cat:
        category = st.selectbox("Disease Category", ["All Users", "Diabetes", "Liver", "Heart", "Mental Health"], key="dir_cat")
    with col_sort:
        sort_by = st.selectbox("Sort By", ["Newest First", "Oldest First", "Name A-Z", "Risk: High to Low"], key="dir_sort")
    
    # Fetch patients
    patients = api_client.get_patients(category=category, sort=sort_by)
    
    if patients:
        # Search filter
        search_query = col_search.text_input("Search by Name or ABHA ID", placeholder="Search...", key="dir_search")
        if search_query:
            patients = [p for p in patients if search_query.lower() in p.get('name', '').lower() or search_query in p.get('abha_id', '')]
        
        # Display Table
        st.write(f"Showing {len(patients)} patients")
        
        display_data = []
        for p in patients:
            display_data.append({
                "ABHA ID": p.get("abha_id"),
                "Name": p.get("name"),
                "Age": p.get("age"),
                "Gender": p.get("gender"),
                "Created": datetime.fromisoformat(p.get("created_at").replace('Z', '+00:00')).strftime("%Y-%m-%d") if p.get("created_at") else "N/A"
            })
        
        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Selection and Actions
        st.subheader("Actions")
        col_sel, col_act = st.columns([2, 1])
        # Use patient_id (int) as value, but show name and abha_id for clarity
        selected_p_id = col_sel.selectbox(
            "Select Patient to View/Edit", 
            [p.get("patient_id") for p in patients], 
            format_func=lambda x: next((f"{p.get('name')} ({p.get('abha_id')})" for p in patients if p.get("patient_id") == x), str(x)), 
            key="dir_select"
        )
        
        if col_act.button("👁️ View Full Profile", use_container_width=True, key="dir_view_btn"):
            st.session_state.view_patient_id = selected_p_id
            set_view("patient_detail")
            
    else:
        st.info("No patients found with current filters.")
        if st.button("Register First Patient", key="dir_reg_btn"):
            set_view("add_user")

# --- View: Register Patient ---
elif st.session_state.admin_view == "add_user":
    st.button("🏠 Back", on_click=set_view, args=("main",), key="reg_back_btn")
    st.title("➕ Register New Patient")
    
    # Multi-step Form
    step = st.session_state.add_user_step
    
    # Progress Bar
    cols_prog = st.columns(3)
    with cols_prog[0]: st.markdown(f"**Step 1: Bio** {'✅' if step > 1 else '🔵'}")
    with cols_prog[1]: st.markdown(f"**Step 2: Vitals** {'✅' if step > 2 else '⚪'}")
    with cols_prog[2]: st.markdown(f"**Step 3: Review** {'✅' if step > 3 else '⚪'}")
    st.progress(step / 3)
    
    if "reg_data" not in st.session_state:
        st.session_state.reg_data = {}

    if step == 1:
        st.subheader("Basic Information")
        with st.form("reg_step1"):
            col1, col2 = st.columns(2)
            name = col1.text_input("Full Name", value=st.session_state.reg_data.get("name", ""), key="reg_name")
            abha_id = col2.text_input("ABHA ID (14 digits)", value=st.session_state.reg_data.get("abha_id", ""), max_chars=14, key="reg_abha")
            
            col3, col4, col5 = st.columns(3)
            age = col3.number_input("Age", min_value=1, max_value=120, value=st.session_state.reg_data.get("age", 30), key="reg_age")
            gender = col4.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(st.session_state.reg_data.get("gender", "Male")), key="reg_gender")
            state = col5.selectbox("State", utils.INDIAN_STATES, index=utils.INDIAN_STATES.index(st.session_state.reg_data.get("state", "Maharashtra")), key="reg_state")
            
            password = st.text_input("Set Portal Password", type="password", help="If empty, default ABHAID@Default123 will be used.", key="reg_pass")
            
            if st.form_submit_button("Next ➡️"):
                if not name or len(abha_id) != 14 or not abha_id.isdigit():
                    st.error("Please provide a valid Name and 14-digit ABHA ID.")
                else:
                    st.session_state.reg_data.update({
                        "name": name, "abha_id": abha_id, "age": age, 
                        "gender": gender, "state": state, "password": password
                    })
                    st.session_state.add_user_step = 2
                    st.rerun()

    elif step == 2:
        st.subheader("Initial Vitals & Health Context")
        with st.form("reg_step2"):
            col1, col2 = st.columns(2)
            height = col1.number_input("Height (cm)", value=st.session_state.reg_data.get("height", 160.0), key="reg_height")
            weight = col2.number_input("Weight (kg)", value=st.session_state.reg_data.get("weight", 60.0), key="reg_weight")
            
            st.info("Additional health context helps in better initial screening.")
            lifestyle = st.selectbox("Primary Lifestyle", ["Sedentary", "Active", "Mixed"], index=["Sedentary", "Active", "Mixed"].index(st.session_state.reg_data.get("lifestyle", "Mixed")), key="reg_lifestyle")
            
            cols = st.columns(2)
            if cols[0].form_submit_button("⬅️ Back"):
                st.session_state.add_user_step = 1
                st.rerun()
            if cols[1].form_submit_button("Review ➡️"):
                st.session_state.reg_data.update({"height": height, "weight": weight, "lifestyle": lifestyle})
                st.session_state.add_user_step = 3
                st.rerun()

    elif step == 3:
        st.subheader("Review Registration")
        st.json(st.session_state.reg_data)
        
        cols = st.columns(2)
        if cols[0].button("⬅️ Edit", key="reg_edit_btn"):
            st.session_state.add_user_step = 1
            st.rerun()
        if cols[1].button("🚀 Complete Registration", type="primary", key="reg_submit_btn"):
            with st.spinner("Creating patient record..."):
                result = api_client.add_patient(st.session_state.reg_data)
                if result:
                    st.success(f"Patient {st.session_state.reg_data['name']} registered successfully!")
                    time.sleep(1.5)
                    st.session_state.add_user_step = 1
                    st.session_state.reg_data = {}
                    set_view("view_patients")

# --- View: Patient Detail ---
elif st.session_state.admin_view == "patient_detail":
    patient_id = st.session_state.view_patient_id
    if not patient_id:
        set_view("view_patients")
    
    st.button("⬅️ Back to Directory", on_click=set_view, args=("view_patients",), key="detail_back_btn")
    
    # Fetch data
    with st.spinner("Loading clinical profile..."):
        p = api_client.get_patient_details(patient_id)
    
    if p:
        st.title(f"Profile: {p.get('name')}")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f"""
            <div class="glass-card" style="padding: 1.5rem;">
                <h3>Demographics</h3>
                <p><b>ABHA ID:</b> {p.get('abha_id')}</p>
                <p><b>Age/Gender:</b> {p.get('age')} / {p.get('gender')}</p>
                <p><b>Location:</b> {p.get('state')}</p>
                <p><b>Registered:</b> {p.get('created_at')[:10]}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("📝 Edit Profile", use_container_width=True, key="detail_edit_btn"):
                st.session_state.edit_patient_data = p
                set_view("edit_patient")
            
            if st.button("📄 Generate PDF Report", use_container_width=True, key="detail_pdf_btn"):
                with st.spinner("Generating PDF report..."):
                    pdf_content = api_client.get_pdf_report(patient_id, ["Overview", "Diabetes", "Liver", "Heart", "Mental Health"])
                    if pdf_content:
                        st.success("✅ Report generated successfully!")
                        st.download_button(
                            label="⬇️ Download PDF Report",
                            data=pdf_content,
                            file_name=f"Health_Report_{p.get('abha_id')}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            key="detail_download_btn"
                        )
                    else:
                        st.error("❌ Failed to generate PDF report.")
        
        with col2:
            st.subheader("Clinical Summary")
            latest_pred = api_client.get_latest_prediction(patient_id)
            utils.display_risk_assessment(latest_pred)
            
            st.subheader("📝 Perform Clinical Assessment")
            st.info("Input clinical vitals to update the patient's risk profile and enable ML screening.")
            
            assessment_type = st.radio(
                "Select Assessment Type",
                ["Diabetes", "Heart", "Liver", "Mental Health"],
                horizontal=True,
                key="admin_assess_type"
            )
            
            if assessment_type == "Diabetes":
                with st.form("admin_diabetes_form"):
                    col_d1, col_d2 = st.columns(2)
                    glucose = col_d1.number_input("Glucose Level (mg/dL)", 0.0, 500.0, 100.0)
                    bp = col_d2.number_input("Blood Pressure (mm Hg)", 0.0, 250.0, 80.0)
                    insulin = col_d1.number_input("Insulin Level (mu U/ml)", 0.0, 1000.0, 30.0)
                    skin = col_d2.number_input("Skin Thickness (mm)", 0.0, 100.0, 20.0)
                    
                    is_pregnant = st.checkbox("Is Pregnant?", value=False)
                    has_history = st.checkbox("Family History of Diabetes?", value=False)
                    
                    if st.form_submit_button("Save Diabetes Data", type="primary", use_container_width=True):
                        res = api_client.add_assessment(patient_id, "diabetes", {
                            "pregnancy": is_pregnant,
                            "glucose": glucose, 
                            "blood_pressure": bp, 
                            "skin_thickness": skin,
                            "insulin": insulin, 
                            "diabetes_history": has_history
                        })
                        if res:
                            st.success("✅ Diabetes assessment saved!")
                            time.sleep(1)
                            st.rerun()
            
            elif assessment_type == "Heart":
                with st.form("admin_heart_form"):
                    st.write("Vitals & Labs")
                    col_h1, col_h2 = st.columns(2)
                    sys_bp = col_h1.number_input("Systolic BP", 50, 250, 120)
                    dia_bp = col_h2.number_input("Diastolic BP", 30, 150, 80)
                    chol = col_h1.number_input("Total Cholesterol", 100.0, 500.0, 200.0)
                    tg = col_h2.number_input("Triglycerides", 50.0, 500.0, 150.0)
                    ldl = col_h1.number_input("LDL Cholesterol", 20.0, 300.0, 100.0)
                    hdl = col_h2.number_input("HDL Cholesterol", 10.0, 150.0, 50.0)
                    
                    st.write("Risk Factors & History")
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
                    
                    if st.form_submit_button("Save Heart Data", type="primary", use_container_width=True):
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
                        if res:
                            st.success("✅ Heart assessment saved!")
                            time.sleep(1)
                            st.rerun()
            
            elif assessment_type == "Liver":
                with st.form("admin_liver_form"):
                    st.write("Liver function markers")
                    col_l1, col_l2 = st.columns(2)
                    t_bil = col_l1.number_input("Total Bilirubin", 0.1, 15.0, 1.0)
                    d_bil = col_l2.number_input("Direct Bilirubin", 0.1, 10.0, 0.3)
                    alk = col_l1.number_input("Alkaline Phosphatase", 50.0, 1000.0, 100.0)
                    sgpt = col_l2.number_input("SGPT/ALT", 5.0, 500.0, 40.0)
                    sgot = col_l1.number_input("SGOT/AST", 5.0, 500.0, 40.0)
                    t_prot = col_l2.number_input("Total Protein", 1.0, 15.0, 7.0)
                    alb = col_l1.number_input("Albumin", 1.0, 10.0, 4.0)
                    
                    if st.form_submit_button("Save Liver Data", type="primary", use_container_width=True):
                        res = api_client.add_assessment(patient_id, "liver", {
                            "total_bilirubin": t_bil,
                            "direct_bilirubin": d_bil,
                            "alkaline_phosphatase": alk,
                            "sgpt_alamine_aminotransferase": sgpt,
                            "sgot_aspartate_aminotransferase": sgot,
                            "total_protein": t_prot,
                            "albumin": alb
                        })
                        if res:
                            st.success("✅ Liver assessment saved!")
                            time.sleep(1)
                            st.rerun()
            
            elif assessment_type == "Mental Health":
                with st.form("admin_mental_form"):
                    st.write("Clinical Screening Scores")
                    col_m1, col_m2 = st.columns(2)
                    phq = col_m1.number_input("PHQ-9 Score", 0, 27, 5)
                    gad = col_m2.number_input("GAD-7 Score", 0, 21, 5)
                    
                    st.write("Symptoms")
                    s_col1, s_col2 = st.columns(2)
                    dep = s_col1.checkbox("Depressiveness")
                    sui = s_col2.checkbox("Suicidal Ideation")
                    anx = s_col1.checkbox("Anxiousness")
                    slp = s_col2.checkbox("Sleepiness/Insomnia")
                    
                    if st.form_submit_button("Save Mental Health Data", type="primary", use_container_width=True):
                        res = api_client.add_assessment(patient_id, "mental_health", {
                            "phq_score": phq,
                            "gad_score": gad,
                            "depressiveness": dep,
                            "suicidal": sui,
                            "anxiousness": anx,
                            "sleepiness": slp
                        })
                        if res:
                            st.success("✅ Mental health assessment saved!")
                            time.sleep(1)
                            st.rerun()
            
            st.divider()
            if st.button("🧪 Trigger New ML Screening", type="primary", use_container_width=True, key="detail_predict_btn"):
                with st.spinner("Analyzing patient health data..."):
                    res = api_client.trigger_prediction(patient_id)
                    if res:
                        st.success("✅ Screening update complete!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Screening could not be completed.")
                        st.info("💡 Ensure the patient has completed at least one health assessment (Diabetes, Heart, Liver, or Mental Health).")

# --- View: Edit Patient ---
elif st.session_state.admin_view == "edit_patient":
    st.button("⬅️ Back to Profile", on_click=set_view, args=("patient_detail",), key="edit_back_btn")
    st.title("📝 Edit Clinical Profile")
    p = st.session_state.get("edit_patient_data", {})
    
    if not p:
        st.error("No patient data loaded for editing.")
        if st.button("Return to Directory", key="edit_err_btn"): set_view("view_patients")
    else:
        with st.form("edit_patient_form"):
            col1, col2 = st.columns(2)
            new_name = col1.text_input("Name", value=p.get('name'), key="edit_name")
            new_age = col2.number_input("Age", value=p.get('age'), min_value=1, key="edit_age")
            
            new_state = st.selectbox("State", utils.INDIAN_STATES, index=utils.INDIAN_STATES.index(p.get('state')) if p.get('state') in utils.INDIAN_STATES else 0, key="edit_state")
            
            if st.form_submit_button("Save Changes"):
                updated = api_client.update_patient(p.get('patient_id'), {"name": new_name, "age": new_age, "state": new_state})
                if updated:
                    st.success("Changes saved!")
                    time.sleep(1)
                    set_view("patient_detail")

else:
    st.write("View under implementation...")
    if st.button("Back home", key="fallback_home_btn"): set_view("main")