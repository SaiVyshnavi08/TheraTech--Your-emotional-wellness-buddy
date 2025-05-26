from flask import Flask, request, Response, jsonify
import cv2
import requests
import base64
import numpy as np

app = Flask(__name__)

# Initialize the face detector
detector = cv2.FaceDetectorYN.create("model.onnx", "", (300, 300))

# Gemini API key
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

# Function to send image to Gemini API
def ask_gemini(image):
    _, buffer = cv2.imencode('.jpg', image)
    b64 = base64.b64encode(buffer).decode('utf-8')

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": "What emotion do you see in the picture?"},
                    {"inline_data": {"mime_type": "image/jpeg", "data": b64}}
                ]
            }
        ]
    }

    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    else:
        return f"Error: {response.status_code} - {response.text}"

@app.route('/detect_emotion', methods=['POST'])
def detect_emotion():
    file = request.files['image']
    npimg = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    detections = detector.detect(frame)[1]
    if detections is not None:
        for det in detections:
            top_x, top_y, width, height = map(int, det[:4])
            cv2.rectangle(frame, (top_x, top_y), (top_x + width, top_y + height), (255, 0, 0), 2)

    emotion_response = ask_gemini(frame)
    return jsonify({"emotion": emotion_response})

    # Run the Flask app
    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=5000)