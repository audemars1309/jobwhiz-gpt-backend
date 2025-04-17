from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import datetime
import json

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

LOG_FILE = "resume_analysis_log.json"

def log_resume_analysis(entry):
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            json.dump([], f)
    with open(LOG_FILE, "r+") as f:
        data = json.load(f)
        data.append(entry)
        f.seek(0)
        json.dump(data, f, indent=4)

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
You are a professional AI resume evaluator. Analyze the resume below and strictly respond ONLY in this exact JSON format:

{{
  "score": 87,
  "badge": "Impressive Resume",
  "analysis": {{
    "strengths": "Summarize 2-3 key strengths of this resume.",
    "weaknesses": "Summarize 2-3 weaknesses in tone, formatting, or structure.",
    "dislikes": "What might recruiters dislike in this resume?",
    "suggestions": "How can this resume be improved in 3 quick suggestions?"
  }}
}}

Score must be out of 100 based on ATS friendliness, formatting, and recruiter psychology.
Badge must be one of: "Not Recruiter-Friendly", "Almost There", "Impressive Resume", "ATS Optimized".

Do NOT add any comments or extra text. Only valid parsable JSON.

Resume:
{resume_text}
"""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional resume reviewer."},
                {"role": "user", "content": gpt_prompt}
            ],
            temperature=0.7
        )

        content = response.choices[0].message.content.strip()

        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            return jsonify({"error": "AI response was not valid JSON."}), 500

        # Log with timestamp
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "score": result.get("score"),
            "badge": result.get("badge"),
            "resume_excerpt": resume_text[:300]
        }
        log_resume_analysis(log_entry)

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
