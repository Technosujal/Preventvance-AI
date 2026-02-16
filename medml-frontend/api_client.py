import streamlit as st
import requests
import json

import os

# --- BASE_URL ---
# Use environment variable for production, fallback to localhost for development
BASE_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:5000/api/v1")

def get_token():
    """Retrieves the auth token from session state."""
    return st.session_state.get("token")

def get_auth_headers():
    """Returns authorization headers."""
    token = get_token()
    if token:
        headers = {"Authorization": f"Bearer {token}"}
        return headers
    return {}

# --- Authentication ---

def get_doctors():
    """Fetches list of all healthcare workers (admins)."""
    try:
        response = requests.get(f"{BASE_URL}/admins", headers=get_auth_headers())
        response.raise_for_status()
        return response.json().get('admins', [])
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching doctors: {e}")
        return []

def patient_login(abha_id, password):
    """Logs in a patient."""
    try:
        response = requests.post(f"{BASE_URL}/auth/patient/login", json={
            "abha_id": abha_id,
            "password": password
        })
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend server.")
        return None
    except requests.exceptions.RequestException as e:
        try:
            error_msg = e.response.json().get('message', 'Unknown error')
        except:
            error_msg = f"Server error: {e.response.status_code}" if hasattr(e, 'response') else str(e)
        st.error(f"Login Failed: {error_msg}")
        return None

def admin_login(username, password):
    """Logs in an admin."""
    try:
        response = requests.post(f"{BASE_URL}/auth/admin/login", json={
            "username": username,
            "password": password
        })
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend server.")
        return None
    except requests.exceptions.RequestException as e:
        try:
            error_msg = e.response.json().get('message', 'Unknown error')
        except:
            error_msg = f"Server error: {e.response.status_code}" if hasattr(e, 'response') else str(e)
        st.error(f"Login Failed: {error_msg}")
        return None

def admin_register(data):
    """Registers a new admin."""
    try:
        response = requests.post(f"{BASE_URL}/auth/admin/register", json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        try:
            error_data = e.response.json()
            if 'messages' in error_data:
                error_msg = "Validation Errors: "
                for msg in error_data['messages']:
                    field = msg.get('loc', ['unknown'])[-1]
                    err_text = msg.get('msg', 'Invalid value')
                    error_msg += f"{field}: {err_text}; "
                st.error(error_msg)
            else:
                error_msg = error_data.get('message') or "Registration failed."
                st.error(f"Admin Registration Failed: {error_msg}")
        except:
            st.error(f"Registration Failed: {e}")
        return None

def patient_register(data):
    """Registers a new patient."""
    try:
        response = requests.post(f"{BASE_URL}/auth/patient/register", json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        try:
            error_data = e.response.json()
            if 'messages' in error_data:
                error_msg = "Validation Errors: "
                for msg in error_data['messages']:
                    field = msg.get('loc', ['unknown'])[-1]
                    err_text = msg.get('msg', 'Invalid value')
                    error_msg += f"{field}: {err_text}; "
                st.error(error_msg)
            else:
                error_msg = error_data.get('message') or "Registration failed."
                st.error(f"Patient Registration Failed: {error_msg}")
        except:
            st.error(f"Registration Failed: {e}")
        return None

# --- Admin: Dashboard & Patient Management ---

def get_dashboard_stats():
    """Fetches admin dashboard analytics."""
    try:
        response = requests.get(f"{BASE_URL}/dashboard/stats", headers=get_auth_headers())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching stats: {e}")
        return None

def add_patient(data):
    """Adds a new patient."""
    # Map 'state' to 'state_name' for backend
    if 'state' in data:
        data['state_name'] = data.pop('state')
    
    # Ensure height/weight are floats
    if 'height' in data: data['height'] = float(data['height'])
    if 'weight' in data: data['weight'] = float(data['weight'])
    
    # Set default password if missing
    if not data.get('password'):
        data['password'] = f"{data['abha_id']}@Default123"
        
    try:
        response = requests.post(f"{BASE_URL}/patients", json=data, headers=get_auth_headers())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        try:
            error_data = e.response.json()
            if 'messages' in error_data:
                error_msg = "Validation errors: "
                for msg in error_data['messages']:
                    field = msg.get('loc', ['unknown'])[-1] if msg.get('loc') else 'unknown'
                    error_text = msg.get('msg', 'Unknown error')
                    error_msg += f"{field}: {error_text}; "
                st.error(error_msg)
            elif 'message' in error_data:
                st.error(f"Error adding patient: {error_data.get('message')}")
            else:
                st.error(f"Error adding patient: {error_data}")
        except:
            st.error(f"Error adding patient: {e.response.text if hasattr(e, 'response') else str(e)}")
        return None

def update_patient(patient_id, data):
    """Updates an existing patient."""
    # Map 'state' to 'state_name' for backend
    if 'state' in data:
        data['state_name'] = data.pop('state')
        
    try:
        response = requests.put(f"{BASE_URL}/patients/{patient_id}", json=data, headers=get_auth_headers())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error updating patient: {e.response.json().get('message', 'Check fields')}")
        return None

def get_patients(category=None, sort=None):
    """Gets a list of registered patients with filters."""
    params = {}
    if category and category != "All Users":
        category_map = {"diabetes": "diabetes", "liver": "liver", "heart": "heart", "mental health": "mental_health"}
        key = category_map.get(category.lower(), category.lower())
        params['disease'] = key
    if sort:
        sort_map = {
            "newest first": "recently_added",
            "risk: high to low": "high_risk",
            "risk: medium to low": "medium_risk",
            "low risk": "low_risk"
        }
        params['sort'] = sort_map.get(sort.lower(), "recently_added")
        
    try:
        response = requests.get(f"{BASE_URL}/patients", headers=get_auth_headers(), params=params)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and 'data' in data and isinstance(data['data'], list):
            return data['data']
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching patients: {e}")
        return []

# --- Admin & Patient: Assessments ---

def add_assessment(patient_id, assessment_type, data):
    """Adds a new assessment for a patient."""
    try:
        url = f"{BASE_URL}/patients/{patient_id}/assessments/{assessment_type}"
        response = requests.post(url, json=data, headers=get_auth_headers())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        try:
            msg = e.response.json().get('message', 'Check fields')
        except:
            msg = str(e)
        st.error(f"Error saving {assessment_type} data: {msg}")
        return None

def trigger_prediction(patient_id):
    """Triggers the ML prediction pipeline for a patient."""
    try:
        url = f"{BASE_URL}/patients/{patient_id}/predict"
        response = requests.post(url, headers=get_auth_headers())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error triggering prediction: {e}")
        return None

def retry_prediction(patient_id):
    """Retry ML prediction for a patient."""
    try:
        url = f"{BASE_URL}/patients/{patient_id}/predict"
        response = requests.post(url, headers=get_auth_headers())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error retrying prediction: {e}")
        return None

# --- Admin & Patient: Consultations ---

def get_all_consultations():
    """Fetches all consultations (Admin sees all, Patient sees theirs)."""
    try:
        url = f"{BASE_URL}/consultations"
        response = requests.get(url, headers=get_auth_headers())
        response.raise_for_status()
        return response.json().get('consultations', [])
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching consultations: {e}")
        return []

def get_available_slots(doctor_id, date_str):
    """Fetches available 30-min slots for a doctor on a specific date."""
    try:
        url = f"{BASE_URL}/consultations/available-slots"
        params = {"doctor_id": doctor_id, "date": date_str}
        response = requests.get(url, headers=get_auth_headers(), params=params)
        response.raise_for_status()
        return response.json().get('slots', [])
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching available slots: {e}")
        return []

def get_doctor_availability():
    """[Admin Only] Gets the logged-in doctor's availability rules."""
    try:
        url = f"{BASE_URL}/consultations/availability"
        response = requests.get(url, headers=get_auth_headers())
        response.raise_for_status()
        return response.json().get('availabilities', [])
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching availability: {e}")
        return []

def update_doctor_availability(availability_list):
    """[Admin Only] Updates the logged-in doctor's availability."""
    try:
        url = f"{BASE_URL}/consultations/availability"
        response = requests.post(url, json=availability_list, headers=get_auth_headers())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error updating availability: {e}")
        return None

def book_consultation(patient_id, doctor_id, disease, consultation_type, consultation_datetime, notes=None):
    """Books a consultation for a specific slot."""
    data = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "disease": disease,
        "consultation_type": consultation_type,
        "consultation_datetime": consultation_datetime,
        "notes": notes
    }
    try:
        url = f"{BASE_URL}/consultations"
        response = requests.post(url, json=data, headers=get_auth_headers())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        try:
            msg = e.response.json().get('message', str(e))
        except:
            msg = str(e)
        st.error(f"Error booking consultation: {msg}")
        return None

def add_consultation_notes(patient_id, notes):
    """[Admin Only] Adds notes for the doctor."""
    try:
        url = f"{BASE_URL}/consultations/notes"
        response = requests.post(url, json={"patient_id": patient_id, "notes": notes}, headers=get_auth_headers())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error saving notes: {e}")
        return None

def get_my_consultations():
    """[Patient Only] Fetches consultations for the logged-in patient."""
    try:
        url = f"{BASE_URL}/consultations/me"
        response = requests.get(url, headers=get_auth_headers())
        response.raise_for_status()
        return response.json().get('consultations', [])
    except requests.exceptions.RequestException:
        return []

def request_consultation(disease, consultation_type='teleconsultation', notes=None):
    """[Patient Only] Requests a new consultation."""
    try:
        url = f"{BASE_URL}/consultations/request"
        data = {"disease": disease, "consultation_type": consultation_type, "notes": notes}
        response = requests.post(url, json=data, headers=get_auth_headers())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error requesting consultation: {e}")
        return None

def update_consultation_status(consultation_id, status=None, datetime_str=None, notes=None):
    """Updates consultation details (admin or patient)."""
    try:
        url = f"{BASE_URL}/consultations/{consultation_id}"
        data = {}
        if status: data["status"] = status
        if datetime_str: data["consultation_datetime"] = datetime_str
        if notes: data["notes"] = notes
        
        response = requests.patch(url, json=data, headers=get_auth_headers())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error updating consultation: {e}")
        return None

def cancel_consultation(consultation_id):
    """Deletes/Cancels a consultation."""
    try:
        url = f"{BASE_URL}/consultations/{consultation_id}"
        response = requests.delete(url, headers=get_auth_headers())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error cancelling consultation: {e}")
        return None

# --- Patient & Shared: Details & Reports ---

def get_patient_details(patient_id):
    """Fetches all details for a single patient."""
    try:
        url = f"{BASE_URL}/patients/{patient_id}"
        response = requests.get(url, headers=get_auth_headers())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching patient details: {e}")
        return None

def get_latest_prediction(patient_id):
    """Fetches the latest risk prediction for a patient."""
    try:
        url = f"{BASE_URL}/patients/{patient_id}/predictions/latest"
        response = requests.get(url, headers=get_auth_headers())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response.status_code == 404:
            return None
        st.error(f"Error fetching predictions: {e}")
        return None

def get_recommendations(patient_id):
    """Fetches lifestyle recommendations for a patient."""
    try:
        url = f"{BASE_URL}/patients/{patient_id}/recommendations"
        response = requests.get(url, headers=get_auth_headers())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching recommendations: {e}")
        return {"diet": [], "exercise": [], "sleep": [], "lifestyle": []}

def get_pdf_report(patient_id, sections):
    """Downloads the patient report as a PDF."""
    try:
        url = f"{BASE_URL}/patients/{patient_id}/report/pdf"
        response = requests.post(url, json={"sections": sections}, headers=get_auth_headers())
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        st.error(f"Error generating PDF: {e}")
        return None

def share_patient_details(patient_id, sections):
    """Requests a backend-generated share link."""
    try:
        url = f"{BASE_URL}/patients/{patient_id}/share"
        response = requests.post(url, json={"sections": sections}, headers=get_auth_headers())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error sharing details: {e}")
        return None

# --- AI Chatbot ---

def send_chat_message(message, history=None):
    """Sends a message to the AI chatbot."""
    try:
        url = f"{BASE_URL}/chat"
        data = {"message": message, "history": history or []}
        response = requests.post(url, json=data, headers=get_auth_headers())
        response.raise_for_status()
        return response.json().get('response')
    except requests.exceptions.RequestException as e:
        st.error(f"Chat Error: {e}")
        return "I'm sorry, I'm having trouble connecting to my AI core."