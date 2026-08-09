"""
Persevex Telecom Churn Predictor — Post-Deployment Smoke Test Script
Executes automated smoke tests against the deployed or local FastAPI REST API backend
to verify CORS headers, endpoint availability, health checks, prediction accuracy, and schema validation.
"""

import sys
import requests

def run_smoke_test(base_url: str):
    print("\n=======================================================")
    print(f" Executing Post-Deployment Smoke Tests against: {base_url}")
    print("=======================================================\n")

    base_url = base_url.rstrip('/')
    tests_passed = 0
    total_tests = 6

    # 1. Root Endpoint Test
    try:
        r = requests.get(f"{base_url}/", timeout=5.0)
        if r.status_code == 200 and r.json().get("status") == "online":
            print("  [PASS] GET / -> HTTP 200 OK (Status: online)")
            tests_passed += 1
        else:
            print(f"  [FAIL] GET / -> HTTP {r.status_code}: {r.text}")
    except Exception as e:
        print(f"  [FAIL] GET / -> Error: {e}")

    # 2. Health Endpoint Test
    try:
        r = requests.get(f"{base_url}/health", timeout=5.0)
        if r.status_code == 200 and r.json().get("status") == "healthy":
            print("  [PASS] GET /health -> HTTP 200 OK (Status: healthy)")
            tests_passed += 1
        else:
            print(f"  [FAIL] GET /health -> HTTP {r.status_code}: {r.text}")
    except Exception as e:
        print(f"  [FAIL] GET /health -> Error: {e}")

    # 3. OpenAPI Schema Test
    try:
        r = requests.get(f"{base_url}/openapi.json", timeout=5.0)
        if r.status_code == 200 and "paths" in r.json():
            print("  [PASS] GET /openapi.json -> HTTP 200 OK (OpenAPI Schema Valid)")
            tests_passed += 1
        else:
            print(f"  [FAIL] GET /openapi.json -> HTTP {r.status_code}")
    except Exception as e:
        print(f"  [FAIL] GET /openapi.json -> Error: {e}")

    # 4. CORS Preflight Test
    try:
        headers = {
            "Origin": "https://persevex-churn-predictor-ui.onrender.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type"
        }
        r = requests.options(f"{base_url}/predict", headers=headers, timeout=5.0)
        allowed_origin = r.headers.get("Access-Control-Allow-Origin", "")
        if r.status_code == 200 and ("*" in allowed_origin or "persevex-churn-predictor-ui.onrender.com" in allowed_origin):
            print(f"  [PASS] OPTIONS /predict -> HTTP 200 OK (CORS Allowed: {allowed_origin})")
            tests_passed += 1
        else:
            print(f"  [FAIL] OPTIONS /predict -> HTTP {r.status_code}, Origin: {allowed_origin}")
    except Exception as e:
        print(f"  [FAIL] OPTIONS /predict -> Error: {e}")

    # 5. Valid Prediction Test
    payload = {
        "gender": "Female",
        "SeniorCitizen": 0,
        "Partner": "Yes",
        "Dependents": "No",
        "tenure": 1,
        "PhoneService": "Yes",
        "MultipleLines": "No",
        "InternetService": "Fiber optic",
        "OnlineSecurity": "No",
        "OnlineBackup": "No",
        "DeviceProtection": "No",
        "TechSupport": "No",
        "StreamingTV": "No",
        "StreamingMovies": "No",
        "Contract": "Month-to-month",
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check",
        "MonthlyCharges": 85.50,
        "TotalCharges": 85.50
    }
    try:
        r = requests.post(f"{base_url}/predict", json=payload, timeout=5.0)
        if r.status_code == 200 and "probability" in r.json():
            prob = r.json()["probability"]
            pred = r.json()["prediction"]
            print(f"  [PASS] POST /predict -> HTTP 200 OK (Prediction: {pred}, Prob: {prob:.4f})")
            tests_passed += 1
        else:
            print(f"  [FAIL] POST /predict -> HTTP {r.status_code}: {r.text}")
    except Exception as e:
        print(f"  [FAIL] POST /predict -> Error: {e}")

    # 6. Invalid Payload Validation Test
    bad_payload = payload.copy()
    bad_payload["Contract"] = "INVALID_CONTRACT_TYPE"
    try:
        r = requests.post(f"{base_url}/predict", json=bad_payload, timeout=5.0)
        if r.status_code in [400, 422]:
            print(f"  [PASS] POST /predict (Invalid Input) -> HTTP {r.status_code} Clean Error Handled")
            tests_passed += 1
        else:
            print(f"  [FAIL] POST /predict (Invalid Input) -> Unexpected HTTP {r.status_code}: {r.text}")
    except Exception as e:
        print(f"  [FAIL] POST /predict (Invalid Input) -> Error: {e}")

    print("\n=======================================================")
    print(f"  SMOKE TEST SUMMARY: {tests_passed}/{total_tests} Tests Passed")
    print("=======================================================\n")

    if tests_passed < total_tests:
        sys.exit(1)

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    run_smoke_test(target)
