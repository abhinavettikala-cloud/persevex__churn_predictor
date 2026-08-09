"""
Persevex Telecom Churn Predictor — Automated Load Testing Script
Simulates concurrent load requests against the FastAPI POST /predict endpoint
and measures throughput, latency percentiles (p50, p95, p99), and error rates.
"""

import time
import argparse
import statistics
import concurrent.futures
import requests

DEFAULT_PAYLOAD = {
    "gender": "Female",
    "SeniorCitizen": 0,
    "Partner": "Yes",
    "Dependents": "No",
    "tenure": 12,
    "PhoneService": "Yes",
    "MultipleLines": "No",
    "InternetService": "Fiber optic",
    "OnlineSecurity": "No",
    "OnlineBackup": "Yes",
    "DeviceProtection": "No",
    "TechSupport": "No",
    "StreamingTV": "Yes",
    "StreamingMovies": "No",
    "Contract": "Month-to-month",
    "PaperlessBilling": "Yes",
    "PaymentMethod": "Electronic check",
    "MonthlyCharges": 70.35,
    "TotalCharges": 844.20
}

def send_request(url: str):
    start = time.time()
    try:
        resp = requests.post(url, json=DEFAULT_PAYLOAD, timeout=5.0)
        latency = (time.time() - start) * 1000
        return resp.status_code == 200, latency, resp.status_code
    except Exception as e:
        latency = (time.time() - start) * 1000
        return False, latency, 500

def run_load_test(target_url: str, num_requests: int, concurrency: int):
    print(f"\n=======================================================")
    print(f" Launching Load Test against: {target_url}")
    print(f"   Total Requests: {num_requests} | Concurrency: {concurrency}")
    print(f"=======================================================\n")

    latencies = []
    successes = 0
    failures = 0
    status_codes = {}

    start_wall = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(send_request, target_url) for _ in range(num_requests)]
        for future in concurrent.futures.as_completed(futures):
            ok, latency, code = future.result()
            latencies.append(latency)
            status_codes[code] = status_codes.get(code, 0) + 1
            if ok:
                successes += 1
            else:
                failures += 1

    total_wall_sec = time.time() - start_wall
    throughput_rps = num_requests / total_wall_sec if total_wall_sec > 0 else 0

    sorted_lat = sorted(latencies)
    p50 = sorted_lat[int(len(sorted_lat) * 0.50)] if sorted_lat else 0
    p95 = sorted_lat[int(len(sorted_lat) * 0.95)] if sorted_lat else 0
    p99 = sorted_lat[int(len(sorted_lat) * 0.99)] if sorted_lat else 0

    print("=======================================================")
    print("                LOAD TEST RESULTS SUMMARY               ")
    print("=======================================================")
    print(f"  Total Wall Clock Time : {total_wall_sec:.2f} seconds")
    print(f"  Throughput            : {throughput_rps:.2f} req/sec")
    print(f"  Success Rate          : {(successes/num_requests*100):.1f}% ({successes}/{num_requests})")
    print(f"  Error Count           : {failures}")
    print(f"  Status Codes Breakdown: {status_codes}")
    print("-------------------------------------------------------")
    print(f"  Latency p50 (Median)  : {p50:.2f} ms")
    print(f"  Latency p95           : {p95:.2f} ms")
    print(f"  Latency p99           : {p99:.2f} ms")
    print(f"  Mean Latency          : {statistics.mean(latencies):.2f} ms")
    print("=======================================================\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Persevex API Load Tester")
    parser.add_argument("--url", default="http://localhost:8000/predict", help="Prediction API URL endpoint")
    parser.add_argument("--requests", type=int, default=100, help="Total requests to execute")
    parser.add_argument("--concurrency", type=int, default=10, help="Number of concurrent worker threads")
    args = parser.parse_args()

    run_load_test(args.url, args.requests, args.concurrency)
