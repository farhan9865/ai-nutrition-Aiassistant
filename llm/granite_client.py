import os
import requests
from dotenv import load_dotenv

# --------------------------------------------------
# Load environment variables from .env
# --------------------------------------------------

load_dotenv(dotenv_path=".env")

IBM_API_KEY = os.getenv("IBM_API_KEY")
IBM_PROJECT_ID = os.getenv("IBM_PROJECT_ID")
IBM_REGION = os.getenv("IBM_REGION")

if not IBM_API_KEY or not IBM_PROJECT_ID or not IBM_REGION:
    raise RuntimeError(
        "Missing IBM credentials in .env file. "
        "Required: IBM_API_KEY, IBM_PROJECT_ID, IBM_REGION"
    )

BASE_URL = f"https://{IBM_REGION}.ml.cloud.ibm.com"

# --------------------------------------------------
# IAM Token generator
# --------------------------------------------------

def _get_access_token():

    url = "https://iam.cloud.ibm.com/identity/token"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "apikey": IBM_API_KEY,
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey"
    }

    response = requests.post(url, headers=headers, data=data, timeout=30)
    response.raise_for_status()

    return response.json()["access_token"]

# --------------------------------------------------
# Granite inference call
# --------------------------------------------------

def ask_granite(prompt: str) -> str:

    token = _get_access_token()

    url = f"{BASE_URL}/ml/v1/text/generation?version=2024-03-01"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        # ✅ Supported in EU + London
        "model_id": "ibm/granite-3-8b-instruct",

        "input": prompt,

        "project_id": IBM_PROJECT_ID,

        "parameters": {
            # 🔥 enough for full 7-day plans
            "max_new_tokens": 1400,

            "temperature": 0.3,
            "top_p": 0.9,
            "repetition_penalty": 1.05
        }
    }

    r = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=120
    )

    if r.status_code != 200:
        raise RuntimeError(
            f"IBM API error {r.status_code}: {r.text}"
        )

    data = r.json()

    # defensive parsing
    if "results" not in data or not data["results"]:
        raise RuntimeError(f"Unexpected IBM response: {data}")

    return data["results"][0]["generated_text"].strip()
