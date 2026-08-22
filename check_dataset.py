import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("PIONEER_API_KEY")
BASE_URL = "https://api.pioneer.ai"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
DATASET_NAME = "immer-british-classifier"

resp = requests.get(
    f"{BASE_URL}/felix/datasets/{DATASET_NAME}/latest/preview",
    headers=HEADERS
)
print(f"Status: {resp.status_code}")
data = resp.json()
print(json.dumps(data, indent=2)[:3000])