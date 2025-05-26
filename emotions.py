# emotions.py
import cv2
import requests
import base64
import numpy as np

# Initialize the face detector with the YuNet model
detector = cv2.FaceDetectorYN.create("model.onnx", "", (300, 300))


# Set up video capture from camera (index 0 or 1)
cv2.namedWindow("cam")
capture = cv2.VideoCapture(0)


# Check if the camera is accessible
if capture.isOpened():
    rval, frame = capture.read()
    img_w, img_h = frame.shape[1], frame.shape[0]
    detector.setInputSize((img_w, img_h))
else:
    rval = False


# Gemini API key
GEMINI_API_KEY = "AIzaSyDjQoPh0DUe9we7qlMmb1JSYWUiz_vBilQ"


# Function to send image to Gemini API
def ask_gemini(image):
    # Encode the image as a base64 string
    _, buffer = cv2.imencode('.jpg', image)
    b64 = base64.b64encode(buffer).decode('utf-8')


    # Define the API endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"


    # Define the request payload
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": "What emotion do you see in the picture?"},  # Your text prompt
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": b64  # Base64-encoded image
                        }
                    }
                ]
            }
        ]
    }


    # Set headers
    headers = {'Content-Type': 'application/json'}


    # Send the POST request
    response = requests.post(url, json=payload, headers=headers)


    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    else:
        return f"Error: {response.status_code} - {response.text}"


# Main loop for real-time face detection and Gemini analysis
while rval:
    rval, frame = capture.read()
    if not rval:
        break


    # Detect faces in the current frame
    detections = detector.detect(frame)[1]


    if detections is not None:
        for i in range(len(detections)):
            # Convert detection coordinates to integers
            output = [int(x) for x in detections[i, :14]]


            # Extract face bounding box
            top_x, top_y, width, height = output[:4]


            # Extract facial landmark coordinates
            right_eye_x, right_eye_y = output[4:6]
            left_eye_x, left_eye_y = output[6:8]
            nose_tip_x, nose_tip_y = output[8:10]
            mouth_right_corner_x, mouth_right_corner_y = output[10:12]
            mouth_left_corner_x, mouth_left_corner_y = output[12:14]


            # Extract face confidence score
            face_score = detections[i, 14]


            # Draw bounding box around detected face
            cv2.rectangle(frame, (top_x, top_y), (top_x + width, top_y + height), (255, 0, 0), 2)


            # Draw facial landmarks
            cv2.rectangle(frame, (right_eye_x - 2, right_eye_y - 2), (right_eye_x + 2, right_eye_y + 2), (0, 0, 255), 1)
            cv2.rectangle(frame, (left_eye_x - 2, left_eye_y - 2), (left_eye_x + 2, left_eye_y + 2), (0, 0, 255), 1)
            cv2.rectangle(frame, (nose_tip_x - 5, nose_tip_y - 5), (nose_tip_x + 5, nose_tip_y + 5), (0, 255, 0), 1)
            cv2.rectangle(frame, (mouth_left_corner_x, mouth_left_corner_y), (mouth_right_corner_x, mouth_right_corner_y), (100, 100, 100), 2)


            # Display face detection confidence score
            cv2.putText(frame, f"{face_score:.2f}", (top_x, top_y - 5), cv2.FONT_HERSHEY_COMPLEX, 0.4, (255, 0, 0), 1)


    # Show the video feed with detections
    cv2.imshow("cam", frame)


    # Send the current frame to Gemini for analysis when 'g' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('g'):
        response = ask_gemini(frame)
        print(response)


    # Exit loop when 'Esc' key (27) is pressed
    if cv2.waitKey(1) == 27:
        break


# Release resources
capture.release()
cv2.destroyAllWindows()



