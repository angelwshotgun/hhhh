from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import os
from dotenv import load_dotenv
import PIL.Image
import io

# Load environment variables from .env file
load_dotenv()

# Configure the API key
api_key = os.getenv('GEMINI_API_KEY')
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
    
    model = genai.GenerativeModel('gemini-2.5-flash-image')
    
    response = model.generate_content(["result only passport no, country_code: Look for explicit nationality or country mentions in text form.Search for country flags or other national symbols.Check for location information that might suggest a country. Provide the corresponding ISO 3166-1 alpha-3 country code., fullname: Identify and distinguish between last name, middle name(s), and first name.Note capitalization and punctuation in names. After reading, provide the full name in the format: Last Name Middle Name(s) First Name., gender: F/M, dob: dd/mm/yyyy, address", image], stream=True,
                                      safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    },generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "application/json"
    })
    response.resolve()
    return response.text

@app.route('/generate_text2', methods=['POST'])
def generate_text2():
    if 'text' not in request.json:
        return jsonify({'error': 'No text provided'}), 400
    
    input_text = request.json['text']
    
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-flash-latest",
        generation_config=generation_config,
        system_instruction="""Result only
My requirements are:

ID: Extract the booking number from the "From" header in parentheses.
the number day booking CLD if room booked is Classic Double Room, CLP if Classic Premium Room, STU if Studio Room, TRIP if Triple Room, Format: (dd - dd/mm)
NET: Calculate the number of nights between the check-in and check-out dates.
Divide the total net price by the number of nights and then by the number of rooms booked.
Format the result as follows: no rounding, no currency symbols, and use a period (.) as the thousands separator.
Append "(Prepaid)" at the end.

Tên: Provide the name in uppercase.
Total net: Display the total net amount
example
ID: 1234567890
1 CLP (02 - 04/12)
NET: ??? (Prepaid)

Tên: Nas
Total net: 600.000"""
    )

    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    "New Booking from Agoda | AG169D1728475852N3405 (1395998868)\nHộp thư đến\nNội dung cập nhật\n\nno-reply do-not-reply@hotellinksolutions.com\n19:10 Th 4, 9 thg 10 (5 ngày trước)\nđến tôi\n\nDAHLIA HOTEL HANOI\n\nCONGRATULATIONS! You've received a new booking.\nBooking number: AG169D1728475852N3405\nAgoda has sent the confirmation email to the guest.\nFor booking enquiries, cancellations or amendments the guest has been instructed to contact Agoda directly.\nVIEW BOOKING\nYOUR BOOKING\nGuest:    Lesseree Rose Santos (Philippines)\n63 09175045779\nCheck-in:    Saturday, October 12, 2024 from 14:00\nCheck-out:    Tuesday, October 15, 2024 until 12:00\nRooms booked:    1 Studio - Non-refundable\nBooked on:    Wednesday, October 9, 2024\nSource:    Agoda (Agoda Handles the Payment) (booking details)\nTotal net price:    ₫ 3.538.080\nTotal sell price:    ₫ 4.914.000",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "ID: 1395998868\n1 STU (12 - 15/10)\nNET: 1.179.360 (Prepaid)\n\nTên: ROSE SANTOS \nTotal net: 3.538.080 \n",
                ],
            },
        ]
    )
    
    response = chat_session.send_message(input_text)
    return response.text
    
if __name__ == '__main__':
    app.run(debug=True)



