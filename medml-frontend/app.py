import streamlit as st
import api_client
from utils import logout
from theme import apply_light_theme
import requests
import base64

st.set_page_config(
    page_title="HealthCare System", 
    layout="wide", 
    initial_sidebar_state="collapsed",
    page_icon="🩺"
)

# Apply enhanced global theme
apply_light_theme()

def check_backend_status():
    """Check if the backend server is running."""
    try:
        response = requests.get("http://127.0.0.1:5000/api/v1/auth/me", timeout=3)
        return True
    except requests.exceptions.ConnectionError:
        return False
    except:
        return True # Assume running if connection is not refused

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "token" not in st.session_state:
    st.session_state.token = None
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

def handle_patient_login(abha_id, password):
    """Callback for patient login."""
    data = api_client.patient_login(abha_id, password)
    if data:
        st.session_state.logged_in = True
        st.session_state.user_role = "patient"
        st.session_state.token = data.get("access_token")
        st.session_state.user_id = data.get("patient_id")
        st.session_state.user_name = data.get("name")
        st.rerun()

def handle_admin_login(username, password):
    """Callback for admin login."""
    data = api_client.admin_login(username, password)
    if data:
        st.session_state.logged_in = True
        st.session_state.user_role = "admin"
        st.session_state.token = data.get("access_token")
        st.session_state.user_id = data.get("admin_id")
        st.session_state.user_name = data.get("name")
        st.rerun()

def handle_admin_registration(reg_data):
    """Callback for admin registration."""
    # Front-end validation
    pwd = reg_data.get('password', '')
    if len(pwd) < 8:
        st.error("Password must be at least 8 characters long.")
        return
    if not any(c.isupper() for c in pwd) or not any(c.islower() for c in pwd) or \
       not any(c.isdigit() for c in pwd) or not any(c in "@$!%*?&_" for c in pwd):
        st.error("Password must contain: Uppercase, Lowercase, Number, and Special character (@$!%*?&_).")
        return

    data = api_client.admin_register(reg_data)
    if data:
        st.success("Admin registered successfully! You can now log in.")
        st.session_state.auth_mode = "login"
        st.rerun()

def handle_patient_registration(reg_data):
    """Callback for patient registration."""
    # Front-end validation
    pwd = reg_data.get('password', '')
    if len(pwd) < 8:
        st.error("Password must be at least 8 characters long.")
        return
    if not any(c.isupper() for c in pwd) or not any(c.islower() for c in pwd) or \
       not any(c.isdigit() for c in pwd) or not any(c in "@$!%*?&_" for c in pwd):
        st.error("Password must contain: Uppercase, Lowercase, Number, and Special character (@$!%*?&_).")
        return

    data = api_client.patient_register(reg_data)
    if data:
        st.success(f"Patient {reg_data['name']} registered successfully! You can now log in with your ABHA ID.")
        st.session_state.auth_mode = "login"
        st.rerun()

# --- Main Content Area ---
if st.session_state.logged_in:
    # This section is shown briefly before redirect
    st.success(f"Welcome back, {st.session_state.user_name}! Redirecting to your dashboard...")
    
    if st.session_state.user_role == "admin":
        st.switch_page("pages/2_Admin_Dashboard.py")
    else:
        st.switch_page("pages/1_Patient_Dashboard.py")

else:
    # --- Main Auth Interface ---
    import os
    # Dynamically select background based on role
    role = st.session_state.get("login_type", "admin")
    bg_filename = "admin_bg.png" if role == "admin" else "login_bg.png"
    img_path = os.path.join(os.path.dirname(__file__), bg_filename)
    
    # Animated background overlay
    try:
        with open(img_path, "rb") as f:
            bg_data = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{bg_data}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            .stApp::before {{
                content: "";
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(255, 255, 255, 0.4);
                z-index: -1;
            }}
            </style>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading background image: {e}")

    col1, col2, col3 = st.columns([1, 2.5, 1])
    
    with col2:
        st.markdown('<div class="animate-fade-in">', unsafe_allow_html=True)
        
        # Glassmorphism Container Start
        st.markdown(f"""
            <div class="glass-card" style="margin-top: 2rem;">
                <div style="text-align: center; margin-bottom: 2rem;">
                    <div style="font-size: 3.5rem; margin-bottom: 0.5rem; filter: drop-shadow(0 0 20px rgba(0,103,165,0.2));">🩺</div>
                    <h1 style="background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
                               -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                               font-size: 2.5rem; margin-bottom: 0.2rem; letter-spacing: -0.05em;">
                        HealthCare AI
                    </h1>
                    <p style="color: var(--color-text-secondary); font-size: 1rem; font-weight: 500; font-family: var(--font-family-secondary);">
                        { "Join our healthcare community" if st.session_state.auth_mode == "register" else "Early Disease Detection & Prevention" }
                    </p>
                </div>
        """, unsafe_allow_html=True)

        # Backend status check
        if not check_backend_status():
            st.error("⚠️ **Backend Server Offline:** Cannot connect to the server at `http://127.0.0.1:5000`.")
            with st.expander("Troubleshooting"):
                st.code("python medml-backend/run.py", language="bash")
            st.stop()
        
        # Auth Mode Selector
        mode = st.segmented_control(
            "Mode",
            options=["login", "register"],
            format_func=lambda x: "🔐 Sign In" if x == "login" else "📝 Register",
            default=st.session_state.auth_mode,
            key="auth_mode_selector"
        )
        st.session_state.auth_mode = mode
        
        # Role Selector
        login_type = st.segmented_control(
            "Role",
            options=["admin", "patient"],
            format_func=lambda x: "👨‍⚕️ Worker" if x == "admin" else "👤 Patient",
            default=st.session_state.get("login_type", "admin"),
            key="login_type_selector"
        )
        st.session_state.login_type = login_type
        
        st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
        
        # --- LOGIN VIEWS ---
        if st.session_state.auth_mode == "login":
            if st.session_state.login_type == "admin":
                with st.form("admin_login_form", border=False):
                    username = st.text_input("Username / Email", placeholder="admin@healthcare.com", key="admin_username")
                    password = st.text_input("Password", type="password", placeholder="••••••••", key="admin_password")
                    st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
                    submitted = st.form_submit_button("Sign In to Portal", use_container_width=True, type="primary")
                    if submitted:
                        if not username or not password:
                            st.error("Missing credentials.")
                        else:
                            with st.spinner("Authenticating security..."):
                                handle_admin_login(username, password)
                st.markdown('<div style="text-align: center; margin-top: 1rem;"><small style="color: #94a3b8;">Default: <b>admin</b> / <b>Admin123!</b></small></div>', unsafe_allow_html=True)
            
            else: # Patient Login
                with st.form("patient_login_form", border=False):
                    abha_id = st.text_input("ABHA ID", placeholder="12345678901234", max_chars=14, key="patient_abha")
                    password = st.text_input("Access Password", type="password", placeholder="••••••••", key="patient_password")
                    st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
                    submitted = st.form_submit_button("Access Health Dashboard", use_container_width=True, type="primary")
                    if submitted:
                        if len(abha_id) != 14 or not abha_id.isdigit():
                            st.error("Invalid ABHA ID.")
                        elif not password:
                            st.error("Missing password.")
                        else:
                            with st.spinner("Retrieving health records..."):
                                handle_patient_login(abha_id, password)
                st.markdown('<div style="text-align: center; margin-top: 1rem;"><small style="color: #64748b;">Enter your 14-digit ABHA ID to access your records.</small></div>', unsafe_allow_html=True)

        # --- REGISTRATION VIEWS ---
        else:
            if st.session_state.login_type == "admin":
                with st.form("admin_register_form", border=False):
                    name = st.text_input("Full Name", placeholder="Dr. Jane Doe")
                    email = st.text_input("Email Address", placeholder="jane.doe@med.com")
                    username = st.text_input("Username (Optional)", placeholder="janedoe")
                    password = st.text_input("Password", type="password", placeholder="••••••••")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        designation = st.text_input("Designation", placeholder="Medical Officer")
                        contact = st.text_input("Contact Number", placeholder="+91...")
                    with c2:
                        facility = st.text_input("Facility Name", placeholder="Civil Hospital")
                    
                    st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
                    submitted = st.form_submit_button("Register as Worker", use_container_width=True, type="primary")
                    if submitted:
                        if not name or not email or not password:
                            st.error("Please fill in all required fields.")
                        else:
                            reg_data = {
                                "name": name, "email": email, "username": username,
                                "password": password, "designation": designation,
                                "contact_number": contact, "facility_name": facility
                            }
                            handle_admin_registration(reg_data)
            
            else: # Patient Registration
                with st.form("patient_register_form", border=False):
                    name = st.text_input("Full Name", placeholder="John Patient")
                    c1, c2, c3 = st.columns([1, 1, 1])
                    with c1:
                        age = st.number_input("Age", min_value=1, max_value=120, value=30)
                    with c2:
                        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                    with c3:
                        state = st.text_input("State", placeholder="Karnataka")
                    
                    c4, c5 = st.columns(2)
                    with c4:
                        height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=170.0)
                    with c5:
                        weight = st.number_input("Weight (kg)", min_value=10.0, max_value=300.0, value=70.0)
                    
                    abha_id = st.text_input("ABHA ID (14 digits)", placeholder="12345678901234", max_chars=14)
                    password = st.text_input("Set Access Password", type="password", placeholder="••••••••")
                    
                    st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
                    submitted = st.form_submit_button("Create My Account", use_container_width=True, type="primary")
                    if submitted:
                        if not name or not abha_id or not password:
                            st.error("Missing required information.")
                        elif len(abha_id) != 14:
                            st.error("ABHA ID must be exactly 14 digits.")
                        else:
                            reg_data = {
                                "name": name, "age": age, "gender": gender,
                                "height": height, "weight": weight, "abha_id": abha_id,
                                "state_name": state, "password": password
                            }
                            handle_patient_registration(reg_data)

        # Glassmorphism Container End
        st.markdown('</div></div>', unsafe_allow_html=True)

    # Footer
    st.markdown(f"""
    <div style='text-align: center; color: #94a3b8; margin-top: 3rem; font-size: 0.85rem; font-weight: 500;'>
        Powered by PreventVance-AI • SECURE CONNECTION ESTABLISHED
    </div>
    """, unsafe_allow_html=True)