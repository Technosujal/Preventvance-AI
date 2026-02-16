import requests
import json

BASE_URL = "http://127.0.0.1:5000/api/v1"

def debug_response():
    # Login
    resp = requests.post(f"{BASE_URL}/auth/admin/login", json={"username": "admin", "password": "Admin123!"})
    token = resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get Patients
    resp = requests.get(f"{BASE_URL}/patients", headers=headers)
    data = resp.json()
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    debug_response()
