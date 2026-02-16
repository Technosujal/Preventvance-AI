import requests
import json
import random

BASE_URL = "http://127.0.0.1:5000/api/v1"

def test_single_prediction():
    print("Testing Single Disease Prediction...")
    
    # 1. Login
    resp = requests.post(f"{BASE_URL}/auth/admin/login", json={"username": "admin", "password": "Admin123!"})
    if resp.status_code != 200:
        print("Login failed")
        return
    token = resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Create a dummy patient
    abha_id = f"{random.randint(10000000000000, 99999999999999)}"
    patient_data = {
        "name": f"Test Patient {abha_id[-4:]}",
        "abha_id": abha_id,
        "password": "Password123!",
        "age": 45,
        "gender": "Male",
        "height": 175,
        "weight": 70,
        "state_name": "Maharashtra"
    }
    resp = requests.post(f"{BASE_URL}/patients", json=patient_data, headers=headers)
    if resp.status_code != 201:
        print(f"Create patient failed: {resp.text}")
        return
    patient_id = resp.json().get("patient_id")
    print(f"Created patient ID: {patient_id}")
    
    # 3. Add ONLY Diabetes Assessment
    diabetes_data = {
        "pregnancy": False,
        "glucose": 120,
        "blood_pressure": 80,
        "skin_thickness": 20,
        "insulin": 80,
        "diabetes_history": False
    }
    resp = requests.post(f"{BASE_URL}/patients/{patient_id}/assessments/diabetes", json=diabetes_data, headers=headers)
    if resp.status_code != 201:
        print(f"Add diabetes assessment failed: {resp.text}")
        return
    print("Added Diabetes Assessment")
    
    # 4. Trigger Prediction (Should succeed now)
    print("Triggering Prediction (Partial)...")
    resp = requests.post(f"{BASE_URL}/patients/{patient_id}/predict", headers=headers)
    
    if resp.status_code == 200:
        print("✅ Prediction Successful!")
        data = resp.json().get("predictions", {})
        print(json.dumps(data, indent=2))
        
        # Verify diabetes is present and others are None
        if data.get("diabetes_risk_score") is not None and data.get("liver_risk_score") is None:
             print("✅ Verified: Diabetes score present, Liver score absent.")
        else:
             print("❌ Verification Failed: Unexpected scores.")
    else:
        print(f"❌ Prediction Failed: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    test_single_prediction()
