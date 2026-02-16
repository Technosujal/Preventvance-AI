import requests
import json

BASE_URL = "http://127.0.0.1:5000/api/v1"

def test_api():
    print("Testing API Routes...")
    
    # 1. Login (Admin) - Required to get token
    print("\n1. Testing Admin Login...")
    try:
        resp = requests.post(f"{BASE_URL}/auth/admin/login", json={"username": "admin", "password": "Admin123!"})
        if resp.status_code == 200:
            token = resp.json().get("access_token")
            print("✅ Admin Login Successful")
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"❌ Admin Login Failed: {resp.status_code} - {resp.text}")
            return
    except Exception as e:
        print(f"❌ Admin Login Error: {e}")
        return

    # 2. Get Patients
    print("\n2. Testing Get Patients...")
    try:
        resp = requests.get(f"{BASE_URL}/patients", headers=headers)
        if resp.status_code == 200:
            print(f"✅ Get Patients Successful: {len(resp.json().get('data', []))} patients found")
            patients = resp.json().get('data', [])
            patient_id = patients[0]['patient_id'] if patients else 62
        else:
            print(f"❌ Get Patients Failed: {resp.status_code} - {resp.text}")
            patient_id = 62
    except Exception as e:
        print(f"❌ Get Patients Error: {e}")
        patient_id = 62

    # 3. Get Patient Details
    print(f"\n3. Testing Get Patient Details (ID: {patient_id})...")
    try:
        resp = requests.get(f"{BASE_URL}/patients/{patient_id}", headers=headers)
        if resp.status_code == 200:
            print("✅ Get Patient Details Successful")
        else:
            print(f"❌ Get Patient Details Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Get Patient Details Error: {e}")

    # 4. Trigger Prediction
    print(f"\n4. Testing Trigger Prediction (ID: {patient_id})...")
    try:
        resp = requests.post(f"{BASE_URL}/patients/{patient_id}/predict", headers=headers)
        if resp.status_code == 200:
            print("✅ Trigger Prediction Successful")
            print(json.dumps(resp.json(), indent=2))
        else:
            print(f"❌ Trigger Prediction Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Trigger Prediction Error: {e}")

    # 5. Get Latest Prediction
    print(f"\n5. Testing Get Latest Prediction (ID: {patient_id})...")
    try:
        resp = requests.get(f"{BASE_URL}/patients/{patient_id}/predictions/latest", headers=headers)
        if resp.status_code == 200:
            print("✅ Get Latest Prediction Successful")
        elif resp.status_code == 404:
            print("⚠️ No prediction found (Expected if none created)")
        else:
            print(f"❌ Get Latest Prediction Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Get Latest Prediction Error: {e}")

if __name__ == "__main__":
    test_api()
