from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import os
from dotenv import load_dotenv
import PIL.Image
import io
import json

# Load environment variables from .env file
load_dotenv()

# Configure the API key
api_key = os.getenv('API_KEY')
if api_key is None:
    raise ValueError("No API key found in environment variables.")

genai.configure(api_key=api_key)

app = Flask(__name__)
CORS(app)

@app.route('/')
def serve_frontend():
    return render_template('index.html')

@app.route('/generate_text', methods=['POST'])
def generate_text():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    image_file = request.files['image']
    image = PIL.Image.open(io.BytesIO(image_file.read()))
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    response = model.generate_content([" result only passport no, country code 3 digit, fullname, gender, dob dd/mm/yyyy, address", image], stream=True,
                                      safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE
    })
    response.resolve()
    data = json.loads(response.text)

    for value in data.values():
        print(value)
    return value
if __name__ == '__main__':
    app.run(debug=True)
