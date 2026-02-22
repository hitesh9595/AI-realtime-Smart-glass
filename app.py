# from flask import Flask, render_template, jsonify, request
# import cv2
# import numpy as np
# import base64
# from ultralytics import YOLO
# import requests
# import pytesseract
# from PIL import Image
# import io
# from threading import Lock
# import os
# import serial
# import time
# import threading

# app = Flask(__name__)
# app.secret_key = "visionassist2025"

# # ==================== GEMINI API ====================
# GEMINI_API_KEY = "AIzaSyDl9ZLcFVhC956XjWpGQ74MamMsCxbwalA"
# GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# # ==================== GROQ API ====================
# GROQ_API_KEY = "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"
# GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# # ==================== ARDUINO SONAR SETUP ====================
# arduino_connected = False
# arduino = None
# latest_distance = "0"
# sonar_active = True
# serial_lock = Lock()  # Add lock for thread safety

# # Configure Tesseract
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# # Load YOLO
# try:
#     yolo_model = YOLO("yolov8n.pt")
#     print("✅ YOLO model loaded")
# except Exception as e:
#     print(f"❌ YOLO error: {e}")
#     yolo_model = None

# # Store states
# latest_objects = []
# camera_active = False
# voice_paused = False
# camera_lock = Lock()

# def init_arduino():
#     """Initialize Arduino connection with proper error handling"""
#     global arduino, arduino_connected, latest_distance
    
#     try:
#         # Try to close any existing connection
#         if arduino and arduino.is_open:
#             arduino.close()
#             time.sleep(1)
        
#         # Attempt new connection
#         arduino = serial.Serial('COM10', 9600, timeout=1)
#         time.sleep(3)  # Wait for Arduino to initialize
        
#         # Clear any pending data
#         arduino.reset_input_buffer()
#         arduino.reset_output_buffer()
        
#         arduino_connected = True
#         print("✅ Arduino connected on COM10")
        
#         # Start reading thread
#         threading.Thread(target=read_serial, daemon=True).start()
        
#     except Exception as e:
#         print(f"❌ Arduino connection error: {e}")
#         arduino_connected = False
#         arduino = None

# def read_serial():
#     """Read data from Arduino"""
#     global latest_distance, sonar_active, arduino_connected
    
#     while sonar_active:
#         if arduino and arduino_connected:
#             try:
#                 with serial_lock:  # Use lock for thread safety
#                     if arduino.in_waiting > 0:
#                         data = arduino.readline().decode().strip()
#                         if data.startswith("Distance:"):
#                             latest_distance = data.replace("Distance:", "").strip()
#                             # Clean up the debug output
#                             if "|" in latest_distance:
#                                 latest_distance = latest_distance.split("|")[0].strip()
#                             print(f"📡 Sonar: {latest_distance} cm")
#             except Exception as e:
#                 print(f"Serial read error: {e}")
#                 arduino_connected = False
#         time.sleep(0.1)

# # Initialize Arduino (only once)
# if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
#     init_arduino()

# def ask_groq(prompt, system_message="You are a helpful assistant."):
#     """Ask Groq API"""
#     headers = {
#         "Authorization": f"Bearer {GROQ_API_KEY}",
#         "Content-Type": "application/json"
#     }
    
#     data = {
#         "model": "mixtral-8x7b-32768",
#         "messages": [
#             {"role": "system", "content": system_message},
#             {"role": "user", "content": prompt}
#         ],
#         "temperature": 0.7,
#         "max_tokens": 300
#     }
    
#     try:
#         response = requests.post(GROQ_URL, json=data, headers=headers, timeout=10)
#         if response.status_code == 200:
#             return response.json()['choices'][0]['message']['content']
#         else:
#             return f"I received your message but couldn't process it properly."
#     except Exception as e:
#         return f"Sorry, I'm having trouble connecting."

# def explain_with_gemini(objects):
#     """Use Gemini for object descriptions"""
#     if not objects:
#         return "I do not see any objects in front of you."
    
#     prompt = f"Describe what a blind person would need to know about: {', '.join(objects)}. Be brief and helpful."
    
#     payload = {
#         "contents": [{"parts": [{"text": prompt}]}]
#     }
    
#     try:
#         response = requests.post(
#             f"{GEMINI_URL}?key={GEMINI_API_KEY}",
#             json=payload,
#             headers={"Content-Type": "application/json"},
#             timeout=10
#         )
        
#         if response.status_code == 200:
#             return response.json()["candidates"][0]["content"]["parts"][0]["text"]
#         else:
#             return f"I can see {', '.join(objects)}"
#     except:
#         return f"I can see {', '.join(objects)}"

# def detect_objects(frame):
#     """YOLO detection"""
#     if yolo_model is None:
#         return []
    
#     try:
#         results = yolo_model(frame, conf=0.20, verbose=False)
#         detected = []
        
#         for r in results:
#             for box in r.boxes:
#                 cls_id = int(box.cls[0])
#                 label = yolo_model.names[cls_id]
#                 detected.append(label)
        
#         return list(dict.fromkeys(detected))
#     except:
#         return []

# @app.route('/')
# def home():
#     """Serve the main HTML page"""
#     return render_template('index.html')

# @app.route('/index1')
# def home_alternative():
#     """Alternative sonar test page"""
#     return render_template('index1.html')

# @app.route('/api/analyze-frame', methods=['POST'])
# def analyze_frame():
#     """YOLO detection + Gemini description"""
#     global latest_objects
    
#     try:
#         data = request.get_json()
#         image_data = data.get('image_data', '')
        
#         if ',' in image_data:
#             image_data = image_data.split(',')[1]
        
#         image_bytes = base64.b64decode(image_data)
#         nparr = np.frombuffer(image_bytes, np.uint8)
#         frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
#         detected_objects = detect_objects(frame)
#         description = explain_with_gemini(detected_objects)
        
#         with camera_lock:
#             latest_objects = detected_objects
        
#         return jsonify({
#             "status": "success",
#             "detectedObjects": detected_objects,
#             "audioDescription": description
#         })
        
#     except Exception as e:
#         return jsonify({"status": "error", "error": str(e)}), 500

# @app.route('/api/sonar-distance', methods=['GET'])
# def get_sonar_distance():
#     """Get latest sonar distance reading"""
#     global latest_distance
#     return jsonify({
#         "distance": latest_distance,
#         "connected": arduino_connected
#     })

# @app.route('/distance', methods=['GET'])
# def distance():
#     """Simple sonar endpoint for backward compatibility"""
#     return jsonify({"distance": latest_distance})

# @app.route('/api/extract-text', methods=['POST'])
# def extract_text():
#     """Extract text from document"""
#     try:
#         if 'file' not in request.files:
#             return jsonify({"error": "No file uploaded"}), 400
        
#         file = request.files['file']
#         if file.filename == '':
#             return jsonify({"error": "No file selected"}), 400
        
#         image_bytes = file.read()
#         image = Image.open(io.BytesIO(image_bytes))
        
#         extracted_text = pytesseract.image_to_string(image)
        
#         if not extracted_text.strip():
#             extracted_text = "No text could be extracted from this image. Please try a clearer image."
        
#         return jsonify({
#             "status": "success",
#             "text": extracted_text.strip()
#         })
        
#     except Exception as e:
#         return jsonify({"status": "error", "error": str(e)}), 500

# @app.route('/api/explain-text', methods=['POST'])
# def explain_text():
#     """Explain text using Groq"""
#     try:
#         data = request.get_json()
#         text = data.get('text', '')
#         prompt_type = data.get('prompt', 'simple')
        
#         if not text or text == "No text could be extracted from this image. Please try a clearer image.":
#             return jsonify({
#                 "status": "success",
#                 "explanation": "No text was extracted from the image. Please try uploading a clearer image with text."
#             })
        
#         if prompt_type == 'simple':
#             prompt = f"Explain this text in very simple words for a blind person: {text}"
#             system_msg = "You are helping a blind person understand text from documents. Use simple language."
#         else:
#             prompt = f"Give a brief summary of this text: {text}"
#             system_msg = "You are helping a blind person by summarizing text."
        
#         explanation = ask_groq(prompt, system_msg)
        
#         return jsonify({
#             "status": "success",
#             "explanation": explanation
#         })
        
#     except Exception as e:
#         return jsonify({"status": "error", "error": str(e)}), 500

# @app.route('/api/voice-ask', methods=['POST'])
# def voice_ask():
#     """Voice assistant using Groq"""
#     try:
#         data = request.get_json()
#         question = data.get('question', '')
#         context = data.get('context', '')
        
#         if not question:
#             return jsonify({"error": "No question"}), 400
        
#         if context:
#             prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer briefly and helpfully for a blind person:"
#             system_msg = "You are a voice assistant for blind people. Give clear, concise answers."
#         else:
#             prompt = f"Question from blind person: {question}\n\nAnswer briefly and helpfully:"
#             system_msg = "You are a helpful voice assistant."
        
#         answer = ask_groq(prompt, system_msg)
        
#         return jsonify({
#             "status": "success",
#             "answer": answer
#         })
        
#     except Exception as e:
#         return jsonify({"status": "error", "error": str(e)}), 500

# @app.route('/api/geocode', methods=['POST'])
# def geocode():
#     """Convert address to coordinates"""
#     try:
#         data = request.get_json()
#         address = data.get('address', '')
        
#         url = "https://nominatim.openstreetmap.org/search"
#         params = {'q': address, 'format': 'json', 'limit': 1}
#         headers = {'User-Agent': 'VisionAssist/1.0'}
        
#         response = requests.get(url, params=params, headers=headers)
#         data = response.json()
        
#         if data:
#             return jsonify({
#                 "lat": float(data[0]['lat']),
#                 "lon": float(data[0]['lon']),
#                 "display_name": data[0]['display_name']
#             })
#         else:
#             return jsonify({"error": "Location not found"}), 404
            
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route('/api/reverse-geocode', methods=['POST'])
# def reverse_geocode():
#     """Get address from coordinates"""
#     try:
#         data = request.get_json()
#         lat = data.get('lat')
#         lon = data.get('lon')
        
#         url = "https://nominatim.openstreetmap.org/reverse"
#         params = {'lat': lat, 'lon': lon, 'format': 'json'}
#         headers = {'User-Agent': 'VisionAssist/1.0'}
        
#         response = requests.get(url, params=params, headers=headers)
#         data = response.json()
        
#         return jsonify({"address": data.get('display_name', 'Unknown')})
        
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route('/favicon.ico')
# def favicon():
#     return '', 204

# def cleanup():
#     """Cleanup function to close serial port"""
#     global sonar_active, arduino
#     sonar_active = False
#     time.sleep(0.5)  # Give thread time to exit
#     if arduino and arduino.is_open:
#         arduino.close()
#         print("🔌 Arduino connection closed")

# import atexit
# atexit.register(cleanup)

# if __name__ == '__main__':
#     print("="*70)
#     print("🌟 VISIONASSIST AI - FULLY INTEGRATED VERSION")
#     print("="*70)
    
#     print("\n✅ WORKING FEATURES:")
#     print("  • Camera & Object Detection")
#     print("  • GPS Navigation")
#     print("  • Document Reader")
#     print("  • Voice Assistant")
#     print("  • Sonar Detection")
    
#     if arduino_connected:
#         print(f"\n📡 Arduino Status: CONNECTED on COM10")
#     else:
#         print(f"\n📡 Arduino Status: NOT CONNECTED (Running in demo mode)")
    
#     print(f"\n📊 Latest Sonar Reading: {latest_distance} cm")
#     print("\n📡 Server: http://localhost:5000")
#     print("="*70)
    
#     # Create templates folder if it doesn't exist
#     if not os.path.exists('templates'):
#         os.makedirs('templates')
#         print("📁 Created 'templates' folder")
    
#     # Run with debug=False to prevent double initialization
#     app.run(debug=False, host='0.0.0.0', port=5000)





























































from flask import Flask, render_template, jsonify, request
import cv2
import numpy as np
import base64
from ultralytics import YOLO
import requests
import pytesseract
from PIL import Image
import io
from threading import Lock
import os
import serial
import time
import threading

app = Flask(__name__)
app.secret_key = "visionassist2025"

# ==================== GEMINI API ====================
GEMINI_API_KEY = "AIzaSyDl9ZLcFVhC956XjWpGQ74MamMsCxbwalA"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# ==================== GROQ API ====================
GROQ_API_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# ==================== ARDUINO SONAR SETUP ====================
arduino_connected = False
arduino = None
latest_distance = "0"
sonar_active = True
serial_lock = Lock()  # Add lock for thread safety

# Configure Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Load YOLO
try:
    yolo_model = YOLO("yolov8n.pt")
    print("✅ YOLO model loaded")
except Exception as e:
    print(f"❌ YOLO error: {e}")
    yolo_model = None

# Store states
latest_objects = []
camera_active = False
voice_paused = False
camera_lock = Lock()

def init_arduino():
    """Initialize Arduino connection with proper error handling"""
    global arduino, arduino_connected, latest_distance
    
    try:
        # Try to close any existing connection
        if arduino and arduino.is_open:
            arduino.close()
            time.sleep(1)
        
        # Attempt new connection
        arduino = serial.Serial('COM10', 9600, timeout=1)
        time.sleep(3)  # Wait for Arduino to initialize
        
        # Clear any pending data
        arduino.reset_input_buffer()
        arduino.reset_output_buffer()
        
        arduino_connected = True
        print("✅ Arduino connected on COM10")
        
        # Start reading thread
        threading.Thread(target=read_serial, daemon=True).start()
        
    except Exception as e:
        print(f"❌ Arduino connection error: {e}")
        arduino_connected = False
        arduino = None

def read_serial():
    """Read data from Arduino"""
    global latest_distance, sonar_active, arduino_connected
    
    while sonar_active:
        if arduino and arduino_connected:
            try:
                with serial_lock:  # Use lock for thread safety
                    if arduino.in_waiting > 0:
                        data = arduino.readline().decode().strip()
                        if data.startswith("Distance:"):
                            latest_distance = data.replace("Distance:", "").strip()
                            # Clean up the debug output
                            if "|" in latest_distance:
                                latest_distance = latest_distance.split("|")[0].strip()
                            print(f"📡 Sonar: {latest_distance} cm")
            except Exception as e:
                print(f"Serial read error: {e}")
                arduino_connected = False
        time.sleep(0.1)

# Initialize Arduino (only once)
if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    init_arduino()

def ask_groq(prompt, system_message="You are a helpful assistant."):
    """Ask Groq API"""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "mixtral-8x7b-32768",
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 300
    }
    
    try:
        response = requests.post(GROQ_URL, json=data, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"I received your message but couldn't process it properly."
    except Exception as e:
        return f"Sorry, I'm having trouble connecting."

def explain_with_gemini(objects):
    """Use Gemini for object descriptions"""
    if not objects:
        return "I do not see any objects in front of you."
    
    prompt = f"Describe what a blind person would need to know about: {', '.join(objects)}. Be brief and helpful."
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        response = requests.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"I can see {', '.join(objects)}"
    except:
        return f"I can see {', '.join(objects)}"

def detect_objects(frame):
    """YOLO detection"""
    if yolo_model is None:
        return []
    
    try:
        results = yolo_model(frame, conf=0.20, verbose=False)
        detected = []
        
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                label = yolo_model.names[cls_id]
                detected.append(label)
        
        return list(dict.fromkeys(detected))
    except:
        return []

@app.route('/')
def home():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/index1')
def home_alternative():
    """Alternative sonar test page"""
    return render_template('index1.html')

@app.route('/api/analyze-frame', methods=['POST'])
def analyze_frame():
    """YOLO detection + Gemini description"""
    global latest_objects
    
    try:
        data = request.get_json()
        image_data = data.get('image_data', '')
        
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        detected_objects = detect_objects(frame)
        description = explain_with_gemini(detected_objects)
        
        with camera_lock:
            latest_objects = detected_objects
        
        return jsonify({
            "status": "success",
            "detectedObjects": detected_objects,
            "audioDescription": description
        })
        
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/api/sonar-distance', methods=['GET'])
def get_sonar_distance():
    """Get latest sonar distance reading"""
    global latest_distance
    return jsonify({
        "distance": latest_distance,
        "connected": arduino_connected
    })

@app.route('/distance', methods=['GET'])
def distance():
    """Simple sonar endpoint for backward compatibility"""
    return jsonify({"distance": latest_distance})

@app.route('/api/extract-text', methods=['POST'])
def extract_text():
    """Extract text from document"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        extracted_text = pytesseract.image_to_string(image)
        
        if not extracted_text.strip():
            extracted_text = "No text could be extracted from this image. Please try a clearer image."
        
        return jsonify({
            "status": "success",
            "text": extracted_text.strip()
        })
        
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/api/explain-text', methods=['POST'])
def explain_text():
    """Explain text using Groq"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        prompt_type = data.get('prompt', 'simple')
        
        if not text or text == "No text could be extracted from this image. Please try a clearer image.":
            return jsonify({
                "status": "success",
                "explanation": "No text was extracted from the image. Please try uploading a clearer image with text."
            })
        
        if prompt_type == 'simple':
            prompt = f"Explain this text in very simple words for a blind person: {text}"
            system_msg = "You are helping a blind person understand text from documents. Use simple language."
        else:
            prompt = f"Give a brief summary of this text: {text}"
            system_msg = "You are helping a blind person by summarizing text."
        
        explanation = ask_groq(prompt, system_msg)
        
        return jsonify({
            "status": "success",
            "explanation": explanation
        })
        
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/api/voice-ask', methods=['POST'])
def voice_ask():
    """Voice assistant using Groq"""
    try:
        data = request.get_json()
        question = data.get('question', '')
        context = data.get('context', '')
        
        if not question:
            return jsonify({"error": "No question"}), 400
        
        if context:
            prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer briefly and helpfully for a blind person:"
            system_msg = "You are a voice assistant for blind people. Give clear, concise answers."
        else:
            prompt = f"Question from blind person: {question}\n\nAnswer briefly and helpfully:"
            system_msg = "You are a helpful voice assistant."
        
        answer = ask_groq(prompt, system_msg)
        
        return jsonify({
            "status": "success",
            "answer": answer
        })
        
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/api/geocode', methods=['POST'])
def geocode():
    """Convert address to coordinates"""
    try:
        data = request.get_json()
        address = data.get('address', '')
        
        url = "https://nominatim.openstreetmap.org/search"
        params = {'q': address, 'format': 'json', 'limit': 1}
        headers = {'User-Agent': 'VisionAssist/1.0'}
        
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        
        if data:
            return jsonify({
                "lat": float(data[0]['lat']),
                "lon": float(data[0]['lon']),
                "display_name": data[0]['display_name']
            })
        else:
            return jsonify({"error": "Location not found"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reverse-geocode', methods=['POST'])
def reverse_geocode():
    """Get address from coordinates"""
    try:
        data = request.get_json()
        lat = data.get('lat')
        lon = data.get('lon')
        
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {'lat': lat, 'lon': lon, 'format': 'json'}
        headers = {'User-Agent': 'VisionAssist/1.0'}
        
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        
        return jsonify({"address": data.get('display_name', 'Unknown')})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/favicon.ico')
def favicon():
    return '', 204

def cleanup():
    """Cleanup function to close serial port"""
    global sonar_active, arduino
    sonar_active = False
    time.sleep(0.5)  # Give thread time to exit
    if arduino and arduino.is_open:
        arduino.close()
        print("🔌 Arduino connection closed")

import atexit
atexit.register(cleanup)

if __name__ == '__main__':
    print("="*70)
    print("🌟 VISIONASSIST AI - FULLY INTEGRATED VERSION")
    print("="*70)
    
    print("\n✅ WORKING FEATURES:")
    print("  • Camera & Object Detection")
    print("  • GPS Navigation")
    print("  • Document Reader")
    print("  • Voice Assistant")
    print("  • Sonar Detection")
    
    if arduino_connected:
        print(f"\n📡 Arduino Status: CONNECTED on COM10")
    else:
        print(f"\n📡 Arduino Status: NOT CONNECTED (Running in demo mode)")
    
    print(f"\n📊 Latest Sonar Reading: {latest_distance} cm")
    print("\n📡 Server: http://localhost:5000")
    print("="*70)
    
    # Create templates folder if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
        print("📁 Created 'templates' folder")
    
    # Run with debug=False to prevent double initialization
    app.run(debug=False, host='0.0.0.0', port=5000)
