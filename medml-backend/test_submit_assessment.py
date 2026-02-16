
import requests
import json

BASE_URL = "http://127.0.0.1:5000/api/v1"

def test_assessment():
    # 1. Login as admin
    login_resp = requests.post(f"{BASE_URL}/auth/admin/login", json={
        "username": "admin",
        "password": "Admin123!"
    })
    
    if login_resp.status_code != 200:
        print(f"Login failed: {login_resp.text}")
        return
    
    token = login_resp.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Get/Create a patient
    patients_resp = requests.get(f"{BASE_URL}/patients", headers=headers)
    resp_data = patients_resp.json()
    patients = resp_data.get('data', []) if isinstance(resp_data, dict) else resp_data
    
    if not patients:
        print("No patients found. Registering a test patient...")
        reg_data = {
            "name": "Test Patient",
            "age": 30,
            "gender": "Male",
            "height": 170.0,
            "weight": 70.0,
            "abha_id": "99998888777766",
            "state_name": "Maharashtra",
            "password": "Password123!"
        }
        reg_resp = requests.post(f"{BASE_URL}/patients", json=reg_data, headers=headers)
        if reg_resp.status_code != 201:
            print(f"Patient registration failed: {reg_resp.text}")
            return
        patient_id = reg_resp.json().get('patient_id')
    else:
        patient_id = patients[0].get('patient_id')
    
    print(f"Testing with patient: {patient_id}")
    
    # 3. Submit assessment
    assess_data = {
        "pregnancy": False,
        "glucose": 120.5,
        "blood_pressure": 80.0,
        "skin_thickness": 20.0,
        "insulin": 35.0,
        "diabetes_history": True
    }
    
    submit_resp = requests.post(
        f"{BASE_URL}/patients/{patient_id}/assessments/diabetes",
        json=assess_data,
        headers=headers
    )
    
    print(f"Submit Status: {submit_resp.status_code}")
    print(f"Submit Response: {json.dumps(submit_resp.json(), indent=2)}")
    
    if submit_resp.status_code == 201:
        # 4. Get all assessments
        get_resp = requests.get(
            f"{BASE_URL}/patients/{patient_id}/assessments",
            headers=headers
        )
        print(f"Get All Status: {get_resp.status_code}")
        print(f"Get All Response: {json.dumps(get_resp.json(), indent=2)}")

if __name__ == "__main__":
    test_assessment()
