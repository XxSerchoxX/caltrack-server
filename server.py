import os
import json
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*", allow_headers=["Content-Type"])

genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))

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
        contents = body.get("contents", [])
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(contents)
        text = response.text
        resp = jsonify({"candidates": [{"content": {"parts": [{"text": text}]}}]})
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp
    except Exception as e:
        resp = jsonify({"error": str(e)})
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp, 500

@app.route("/", methods=["GET"])
def health():
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
