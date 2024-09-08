import requests

def call_webhook(webhook_url, payload):
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        print(f"Webhook called successfully. Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Failed to call webhook: {e}")
