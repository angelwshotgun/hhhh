from flask import Flask, request, jsonify
import requests
import json
from waitress import serve
from flask_cors import CORS
import os

# Replace with your actual Gemini API key (not Google Cloud Platform key)
API_KEY = os.getenv("GEMINI_API_KEY")

app = Flask(__name__)
cors = CORS(app)

@app.route("/api/check-connection", methods=["GET"])
def check_api_connection():
    try:
        response = requests.get("https://api.gemoni.ai/")
        response.raise_for_status()  # Raise an exception if the status code is not 200
        return jsonify({"status": "success", "message": "Connected to Gemini API"})
    except requests.exceptions.RequestException as e:
        print(f"API Connection Error: {e}")
        return jsonify({"status": "error", "message": "Failed to connect to Gemini API"})

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        try:
            with open("index.html", "r") as f:
                html = f.read()
            return html
        except FileNotFoundError:
            return jsonify({"error": "index.html not found"}), 500

    elif request.method == "POST":
        if "image" not in request.files:
            return jsonify({"error": "Missing image file"}), 400

        image_file = request.files["image"]
        image_data = image_file.read()

        headers = {"Authorization": f"Bearer {API_KEY}",
                   "Content-Type": "application/octet-stream"}
        try:
            response = requests.post(
                "https://api.gemini.ai/v1/vision/pro/text", headers=headers, data=image_data
            )
            response.raise_for_status()  # Raise an exception for non-200 status codes

            response_data = json.loads(response.content.decode('utf-8'))
            text_blocks = response_data['text_blocks']
            extracted_text = ""
            for block in text_blocks:
                extracted_text += block['text'] + "\n"

            return jsonify({"success": True, "text": extracted_text})
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return jsonify({"error": "Failed to extract text"}), 500
        except Exception as e:  # Catch generic exceptions for broader error handling
            print(f"Unexpected Error: {e}")
            return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5000)
