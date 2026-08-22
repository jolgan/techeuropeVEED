import os
import csv
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("PIONEER_API_KEY")
BASE_URL = "https://api.pioneer.ai"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
DATASET_NAME = "immer-british-classifier"

# --- Step 1: Convert dataset.csv to JSONL (single-label classification shape) ---
import random
random.seed(42)

with open("dataset.csv") as f:
    rows = list(csv.DictReader(f))

random.shuffle(rows)  # critical: avoid ordered british-then-american blocks

jsonl_path = "dataset.jsonl"
with open(jsonl_path, "w") as f:
	for r in rows:
		text = r['title']  # titles only — testing if long boilerplate descriptions are drowning the signal
		f.write(json.dumps({"text": text, "label": r["label"]}) + "\n")

print(f"✅ Wrote {len(rows)} rows to {jsonl_path}")

# --- Step 2: Get a presigned upload URL ---
resp = requests.post(
    f"{BASE_URL}/felix/datasets/upload/url",
    headers=HEADERS,
    json={
        "dataset_name": DATASET_NAME,
        "dataset_type": "classification",
        "type": "training",
        "filename": "dataset.jsonl"
    }
)
print(f"\nPresigned URL request status: {resp.status_code}")
print(resp.text)
resp.raise_for_status()
upload_info = resp.json()
presigned_url = upload_info["presigned_url"]
dataset_id = upload_info["dataset_id"]

# --- Step 3: Upload the file directly to S3 ---
with open(jsonl_path, "rb") as f:
    put_resp = requests.put(
        presigned_url,
        data=f,
        headers={"Content-Type": "application/octet-stream"}
    )
print(f"\nS3 upload status: {put_resp.status_code}")
if put_resp.status_code != 200:
    print(f"S3 error response: {put_resp.text[:1000]}")
put_resp.raise_for_status()

# --- Step 4: Trigger processing ---
process_resp = requests.post(
    f"{BASE_URL}/felix/datasets/upload/process",
    headers=HEADERS,
    json={"dataset_id": dataset_id}
)
print(f"\nProcess trigger status: {process_resp.status_code}")
print(process_resp.text)
process_resp.raise_for_status()

# --- Step 5: Poll until dataset is ready ---
print(f"\nPolling dataset status...")
while True:
    status_resp = requests.get(
        f"{BASE_URL}/felix/datasets/{DATASET_NAME}/latest",
        headers=HEADERS
    )
    status_data = status_resp.json()
    status = status_data.get("status", "unknown")
    print(f"  Status: {status}")
    if status == "ready":
        print("✅ Dataset ready!")
        break
    if status == "failed":
        print(f"❌ Dataset failed: {status_data.get('processing_error')}")
        break
    time.sleep(5)

# --- Step 6: Start the training job ---
print("\nStarting training job...")
train_resp = requests.post(
    f"{BASE_URL}/felix/training-jobs",
    headers=HEADERS,
    json={
        "model_name": "immer-british-classifier-v1",
        "base_model": "fastino/gliner2-base-v1",
        "datasets": [{"name": DATASET_NAME}],
        "training_type": "lora",
        "nr_epochs": 15,
        "learning_rate": 5e-5
    }
)
print(f"Training job request status: {train_resp.status_code}")
print(train_resp.text)
train_resp.raise_for_status()
job_id = train_resp.json()["id"]
print(f"\n✅ Job started. ID: {job_id}")

# --- Step 7: Poll until training completes ---
print("\nPolling training status (this may take a few minutes)...")
while True:
    poll_resp = requests.get(f"{BASE_URL}/felix/training-jobs/{job_id}", headers=HEADERS)
    job_data = poll_resp.json()
    status = job_data.get("status", "unknown")
    print(f"  Status: {status}")
    if status in ("complete", "deployed"):
        print(f"\n✅ Training complete!")
        print(json.dumps(job_data.get("metrics", {}), indent=2))
        break
    if status in ("errored", "stopped", "terminated"):
        print(f"\n❌ Training ended with status: {status}")
        print(json.dumps(job_data, indent=2)[:1000])
        break
    time.sleep(15)

print(f"\nSave this job ID for the agent: {job_id}")

# --- Step 8: Sanity-check inference on new examples ---
print("\n--- Sanity check: inference on unseen examples ---")

test_cases = [
    ("The Rest Is Football", "Gary Lineker, Alan Shearer and Micah Richards discuss the weekend's Premier League action from London."),
    ("The Bill Simmons Podcast", "Bill Simmons breaks down the NBA trade deadline with guests from ESPN."),
    ("Grounded with Louis Theroux", "Louis Theroux sits down with a guest for an intimate, wide-ranging conversation recorded in the UK."),
    ("Armchair Expert", "Dax Shepard talks with a Hollywood actor about their career and personal life."),
]

for title, desc in test_cases:
    text = f"{title}. {desc}"
    inf_resp = requests.post(
        f"{BASE_URL}/inference",
        headers=HEADERS,
        json={
            "model_id": job_id,
            "text": text,
            "schema": {
                "classifications": [
                    {"task": "accent", "labels": ["british", "not_british"], "multi_label": False}
                ]
            }
        }
    )
    result = inf_resp.json()
    print(f"\n'{title}' →")
    print(json.dumps(result, indent=2)[:500])