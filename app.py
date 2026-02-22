# # from flask import Flask, request, jsonify, render_template_string
# # import requests
# # import pytesseract
# # from PIL import Image
# # import os
# # import uuid

# # # ================= CONFIG =================

# # WEBHOOK_URL = "https://maagew.app.n8n.cloud/webhook/d504f828-fda0-4ded-84fd-f90e9635e1de"

# # UPLOAD_FOLDER = "uploads"
# # os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# # # ==========================================

# # app = Flask(__name__)
# # app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# # # ================= FRONTEND =================

# # HTML_PAGE = """
# # <!DOCTYPE html>
# # <html>
# # <head>
# # <title>VisionAssist</title>
# # <style>
# # body{font-family:Arial;background:#111;color:white;text-align:center}
# # input,button{padding:10px;margin:5px;width:80%}
# # #chat{height:300px;overflow:auto;border:1px solid white;padding:10px}
# # </style>
# # </head>

# # <body>

# # <h2>VisionAssist for Blind Users</h2>

# # <div id="chat"></div>

# # <input id="msg" placeholder="Type message...">
# # <br>
# # <button onclick="sendMsg()">Send</button>

# # <br><br>

# # <input type="file" id="file">
# # <br>
# # <button onclick="uploadFile()">Upload File</button>

# # <script>

# # function addChat(text){
# #   document.getElementById("chat").innerHTML += "<p>"+text+"</p>";
# # }

# # function sendMsg(){

# #   let msg = document.getElementById("msg").value;

# #   fetch("/send",{
# #     method:"POST",
# #     headers:{"Content-Type":"application/json"},
# #     body:JSON.stringify({message:msg})
# #   })
# #   .then(r=>r.json())
# #   .then(d=>{
# #     addChat("You: "+msg);
# #     addChat("AI: "+d.reply);
# #   });

# #   document.getElementById("msg").value="";
# # }


# # function uploadFile(){

# #   let f = document.getElementById("file").files[0];

# #   let form = new FormData();
# #   form.append("file",f);

# #   fetch("/upload",{
# #     method:"POST",
# #     body:form
# #   })
# #   .then(r=>r.json())
# #   .then(d=>{
# #     addChat("File Text: "+d.text);
# #     addChat("AI: "+d.reply);
# #   });
# # }

# # </script>

# # </body>
# # </html>
# # """


# # # ================= ROUTES =================

# # @app.route("/")
# # def home():
# #     return render_template_string(HTML_PAGE)


# # # ============ SEND MESSAGE TO WEBHOOK ============

# # @app.route("/send", methods=["POST"])
# # def send_message():

# #     data = request.json
# #     user_msg = data.get("message","")

# #     payload = {
# #         "type":"text",
# #         "message":user_msg
# #     }

# #     try:

# #         r = requests.post(WEBHOOK_URL,json=payload,timeout=20)

# #         if r.status_code != 200:
# #             return jsonify({"reply":"Webhook Error"})

# #         result = r.json()

# #         reply = result.get("reply","No response")

# #         return jsonify({"reply":reply})

# #     except Exception as e:
# #         return jsonify({"reply":"Server Error"})


# # # ============ FILE UPLOAD + OCR + AI ============

# # @app.route("/upload", methods=["POST"])
# # def upload_file():

# #     if "file" not in request.files:
# #         return jsonify({"error":"No file"})

# #     f = request.files["file"]

# #     name = str(uuid.uuid4())+"_"+f.filename
# #     path = os.path.join(UPLOAD_FOLDER,name)

# #     f.save(path)


# #     # ---------- OCR ----------
# #     try:
# #         img = Image.open(path)
# #         text = pytesseract.image_to_string(img)

# #     except:
# #         text = "Cannot extract text"


# #     # ---------- Send To Webhook ----------

# #     payload = {
# #         "type":"file",
# #         "text":text
# #     }

# #     try:

# #         r = requests.post(WEBHOOK_URL,json=payload,timeout=30)

# #         if r.status_code != 200:
# #             return jsonify({"text":text,"reply":"Webhook Error"})

# #         result = r.json()

# #         reply = result.get("reply","No response")

# #     except:
# #         reply = "Server Error"


# #     return jsonify({
# #         "text":text,
# #         "reply":reply
# #     })


# # # ================= START =================

# # if __name__ == "__main__":
# #     app.run(host="0.0.0.0",port=5000,debug=True)










# from flask import Flask, render_template
# app = Flask(__name__)

# @app.route('/')
# def home():
#     return render_template('index.html')

# if __name__ == '__main__':
#     print("🚀 Server: http://localhost:5000")
#     app.run(debug=True, port=5000)






















import requests

API_KEY = "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"
url = "https://api.groq.com/openai/v1/chat/completions"

# Models to test (current as of 2024)
models_to_test = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "gemma2-9b-it",
    "mixtral-8x7b-32768"  # This will fail (decommissioned)
]

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

for model in models_to_test:
    print(f"\nTesting: {model}")
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Say 'hello' in one word"}],
        "temperature": 0.7
    }
    
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ WORKING!")
        print(f"Response: {response.json()['choices'][0]['message']['content']}")
        break
    else:
        print(f"❌ Failed: {response.text}")
