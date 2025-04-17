from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import datetime
import json
import fitz  # PyMuPDF

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/", methods=["GET"])
def home():
    return "JobWhiz GPT Resume Analyzer is running!"

@app.route("/analyze", methods=["POST"])
def analyze_resume():
    try:
        if "resume" not in request.files:
            return jsonify({"error": "No resume file uploaded"}), 400

        resume_file = request.files["resume"]

        # Extract text from PDF using PyMuPDF
        def extract_text_from_pdf(file):
            text = ""
            with fitz.open(stream=file.read(), filetype="pdf") as doc:
                for page in doc:
                    text += page.get_text()
            return text

        resume_text = extract_text_from_pdf(resume_file)

        prompt = f"""You are a resume expert AI. Read the resume below and return only valid JSON.

{{
  "score": 0 to 100 (based on formatting, keyword usage, ATS compatibility, etc),
  "badge": "Not Recruiter-Friendly" or "Almost There" or "Impressive Resume" or "ATS Optimized",
  "analysis": {{
    "strengths": "List 2-3 key strengths",
    "weaknesses": "List 2-3 key weaknesses",
    "dislikes": "What might recruiters dislike?",
    "suggestions": "3 solid improvement tips"
  }}
}}

ONLY return valid JSON. No explanations. Resume:
{resume_text}
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional resume reviewer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        content = response.choices[0].message.content.strip()

        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            return jsonify({"error": "AI response was not valid JSON."}), 500

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
