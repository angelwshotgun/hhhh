from flask import Flask, request, jsonify
import requests
import json
from waitress import serve
from flask_cors import CORS


# Replace with your actual API key
API_KEY = "AIzaSyBkK6TPvo7jlcLzlX37-ZJa8ONP0yns2RM"

app = Flask(__name__)
cors = CORS(app)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        # Display the HTML form
        try:
            with open("index.html", "r") as f:
                html = f.read()
            return html
        except FileNotFoundError:
            return jsonify({"error": "index.html not found"}), 500

    elif request.method == "POST":
        # Process the uploaded image and extract text
        if "image" not in request.files:
            return jsonify({"error": "Missing image file"}), 400

        image_file = request.files["image"]
        image_data = image_file.read()

        # Send API request and extract text
        headers = {"Authorization": f"Bearer {API_KEY}",
                   "Content-Type": "application/octet-stream"}
        try:
            response = requests.post(
                "https://api.gemini.ai/v1/vision/pro/text", headers=headers, data=image_data
            )
            response.raise_for_status()  # Raise exception for non-200 status codes

            response_data = json.loads(response.content.decode('utf-8'))
            text_blocks = response_data['text_blocks']
            extracted_text = ""
            for block in text_blocks:
                extracted_text += block['text'] + "\n"
            return jsonify({"text": extracted_text})
        except requests.exceptions.RequestException as e:  # Catch various request errors
            print(f"API Error: {e}")
            return jsonify({"error": "Failed to extract text"}), 500

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5000)  # Serve on all interfaces with port 5000
