import os
import requests
import streamlit as st

# --------------------------------------------------
# Load credentials from Streamlit Secrets
# --------------------------------------------------

IBM_API_KEY = st.secrets.get("IBM_API_KEY")
IBM_PROJECT_ID = st.secrets.get("IBM_PROJECT_ID")
IBM_REGION = st.secrets.get("IBM_REGION")

if not IBM_API_KEY or not IBM_PROJECT_ID or not IBM_REGION:
    raise RuntimeError(
        "Missing IBM credentials in Streamlit Secrets. "
        "Add IBM_API_KEY, IBM_PROJECT_ID, IBM_REGION in Settings."
    )

BASE_URL = f"https://{IBM_REGION}.ml.cloud.ibm.com"


# --------------------------------------------------
# IAM Token
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

    r = requests.post(url, headers=headers, data=data, timeout=30)
    r.raise_for_status()

    return r.json()["access_token"]


# --------------------------------------------------
# Granite Call
# --------------------------------------------------

def ask_granite(prompt: str) -> str:

    token = _get_access_token()

    url = f"{BASE_URL}/ml/v1/text/generation?version=2024-03-01"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "model_id": "ibm/granite-3-8b-instruct",
        "input": prompt,
        "project_id": IBM_PROJECT_ID,
        "parameters": {
            "max_new_tokens": 1200,
            "temperature": 0.3,
            "top_p": 0.9,
        }
    }

    r = requests.post(url, headers=headers, json=payload, timeout=120)

    if r.status_code != 200:
        raise RuntimeError(
            f"IBM API error {r.status_code}: {r.text}"
        )

    data = r.json()

    return data["results"][0]["generated_text"].strip()
