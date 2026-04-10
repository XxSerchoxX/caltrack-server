import os
import json
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        body = request.get_json()
        contents = body.get("contents", [])

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(contents)
        text = response.text

        return jsonify({"candidates": [{"content": {"parts": [{"text": text}]}}]})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def health():
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
