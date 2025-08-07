import os
from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# Hardcoded required keys list here (not from env vars)
REQUIRED_KEYS = [
    "image_path",
    "username",
    "user_id",
    "unsafe_score",
    "is_safe",
    "nsfw_score",
    "text_flags",
    "morse_decoded",
    "rot_decoded",
    "ocr_text",
    "summary"
]

def is_valid_message(message: dict, required_keys: list) -> bool:
    for key in required_keys:
        if key not in message:
            return False
    return True

def send_to_discord_webhook(webhook_url: str, message: dict):
    headers = {"Content-Type": "application/json"}
    content = "New validated message:\n```json\n" + json.dumps(message, indent=2) + "\n```"
    payload = {"content": content}
    response = requests.post(webhook_url, headers=headers, json=payload)
    return response

# Load Discord webhook URL from environment (set in Render dashboard)
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
if not DISCORD_WEBHOOK_URL:
    print("Environment variable 'DISCORD_WEBHOOK_URL' not set.")
    exit(1)

@app.route("/send_message", methods=["POST"])
def send_message():
    if not request.is_json:
        return jsonify({"error": "Invalid content type, expected application/json"}), 400

    message = request.get_json()

    missing_keys = [key for key in REQUIRED_KEYS if key not in message]
    if missing_keys:
        return jsonify({"error": "Missing required keys", "missing_keys": missing_keys}), 400

    response = send_to_discord_webhook(DISCORD_WEBHOOK_URL, message)
    if response.status_code == 204:
        return jsonify({"status": "Message sent successfully"}), 200
    else:
        return jsonify({
            "error": "Failed to send message to Discord webhook",
            "status_code": response.status_code,
            "response": response.text
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
