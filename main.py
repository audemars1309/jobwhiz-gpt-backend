from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import datetime
import json
import re

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return "JobWhiz GPT Resume Analyzer is running!"

@app.route("/analyze", methods=["POST"])
def analyze_resume():
    try:
        if "resume" not in request.files:
            return jsonify({"error": "No resume file provided"}), 400

        resume_file = request.files["resume"]
        resume_text = resume_file.read().decode("utf-8")

        gpt_prompt = f"""
You are an expert resume reviewer. Analyze the resume below and return ONLY a JSON object like this:

{{
  "score": 85,
  "badge": "Impressive Resume",
  "analysis": {{
    "strengths": "Clear formatting, impactful language.",
    "weaknesses": "Lacks measurable achievements.",
    "dislikes": "Overuse of buzzwords.",
    "suggestions": "Add numbers, be concise, tailor to job."
  }}
}}

BADGE must be one of: "Not Recruiter-Friendly", "Almost There", "Impressive Resume", "ATS Optimized".
SCORE must be between 1 and 100.

ONLY return the JSON. No extra commentary.

Resume:
{resume_text}
"""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional resume scoring assistant."},
                {"role": "user", "content": gpt_prompt}
            ],
            temperature=0.4
        )

        content = response.choices[0].message.content.strip()

        # Extract JSON using regex in case GPT adds fluff
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if not json_match:
            return jsonify({"error": "Could not find valid JSON in AI response."}), 500

        cleaned_json = json_match.group()
        result = json.loads(cleaned_json)

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

