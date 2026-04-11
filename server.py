import os
import google.generativeai as genai
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='static')
CORS(app, origins="*", allow_headers=["Content-Type"])

genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))

@app.route("/")
def index():
    return send_from_directory('static', 'index.html')

@app.route("/analyze", methods=["POST", "OPTIONS"])
def analyze():
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        return response, 200
    try:
        body = request.get_json()
        raw_contents = body.get("contents", [])
        gemini_parts = []
        for content in raw_contents:
            for part in content.get("parts", []):
                if "inlineData" in part:
                    gemini_parts.append({
                        "inline_data": {
                            "mime_type": part["inlineData"]["mimeType"],
                            "data": part["inlineData"]["data"]
                        }
                    })
                elif "inline_data" in part:
                    gemini_parts.append(part)
                elif "text" in part:
                    gemini_parts.append({"text": part["text"]})
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content({"parts": gemini_parts})
        text = response.text
        resp = jsonify({"candidates": [{"content": {"parts": [{"text": text}]}}]})
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp
    except Exception as e:
        resp = jsonify({"error": str(e)})
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp, 500

@app.route("/health", methods=["GET"])
def health():
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
