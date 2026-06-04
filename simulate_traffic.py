import time
import httpx

VALID_API_KEY = "YOUR_GENERATED_API_KEY_HERE"


headers = {"X-API-KEY": VALID_API_KEY}

print("Starting high-end traffic simulation loop...")
for i in range(10):
    try:
        response = httpx.get("http://127.0.0.1:8000/protected-data", headers=headers)
        print(f"Requests {i+1}: Status Code {response.status_code} -> {response.json()}")
    except Exception as e:
        print(f"Network request dropped: {e}")

    time.sleep(1)
