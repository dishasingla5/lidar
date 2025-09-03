#!/usr/bin/env python3

import cv2
import requests
import base64
import json
import numpy as np
from bs4 import BeautifulSoup
from pyzbar.pyzbar import decode

# === Roboflow Configuration ===
ROBOFLOW_API_KEY = "e7aox3QopoiopktQkw7O"
ROBOFLOW_MODEL = "qr-code-test-model-gqax4"
ROBOFLOW_VERSION = "1"
API_URL = f"https://detect.roboflow.com/{ROBOFLOW_MODEL}/{ROBOFLOW_VERSION}?api_key={ROBOFLOW_API_KEY}"

# === Track already seen QR codes ===
seen_codes = set()

# === Fetch content if it's a URL ===
def fetch_data_from_url(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                return response.json()
            elif "text/html" in content_type:
                soup = BeautifulSoup(response.text, "html.parser")
                main_p = soup.find("p")
                body_text = main_p.get_text(strip=True) if main_p else "No text found"
                return body_text
            else:
                return response.text.strip()
        else:
            return f"Failed to fetch data: Status {response.status_code}"
    except Exception as e:
        return f"Error fetching data: {str(e)}"

def is_url(text):
    return text.startswith("http://") or text.startswith("https://")

# === Main QR Scanner ===
def scan_qr_combined():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera not accessible.")
        return

    print("Scanning QR codes with Roboflow model... (Press ESC to exit)")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Resize frame for API
        resized = cv2.resize(frame, (640, 640))

        # Encode to base64
        _, buffer = cv2.imencode('.jpg', resized)
        b64_image = base64.b64encode(buffer).decode("utf-8")

        # Roboflow Detection
        response = requests.post(
            API_URL,
            data=b64_image,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        predictions = response.json().get("predictions", [])

        for pred in predictions:
            x = int(pred['x'] - pred['width'] / 2)
            y = int(pred['y'] - pred['height'] / 2)
            w = int(pred['width'])
            h = int(pred['height'])

            # Crop and decode QR
            crop = resized[y:y + h, x:x + w]
            decoded_objs = decode(crop)

            for obj in decoded_objs:
                qr_data = obj.data.decode('utf-8').strip()
                if qr_data in seen_codes:
                    continue

                seen_codes.add(qr_data)
                print("\n=== New QR Code Detected ===")

                if is_url(qr_data):
                    print(f"QR Content (URL): {qr_data}")
                    result = fetch_data_from_url(qr_data)
                    print(f"Data from URL:\n{result}")
                else:
                    result = qr_data
                    print(f"QR Content (Text): {result}")

                # Draw detection box and text
                cv2.rectangle(resized, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(resized, str(result), (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # Show total count
        cv2.putText(resized, f"Unique QR Codes: {len(seen_codes)}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

        # Display frame
        cv2.imshow("QR Code Scanner (Roboflow + Smart Decode)", resized)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC key
            break

    cap.release()
    cv2.destroyAllWindows()

# === Run the combined scanner ===
if __name__ == "__main__":
    scan_qr_combined()

