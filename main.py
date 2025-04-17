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

        gpt_prompt = f'''
You are a top-tier career advisor and recruiter AI. Analyze the following resume and give:

1. A score out of 100 based on ATS-friendliness, formatting, keyword match, and recruiter appeal.
2. A badge (choose from: 'Not Recruiter-Friendly', 'Almost There', 'Impressive Resume', 'ATS Optimized').
3. Detailed analysis with:
  - Strengths
  - Weaknesses
  - What recruiters might dislike
  - Suggestions to improve

Only return JSON like this:
{{
  "score": 87,
  "badge": "Impressive Resume",
  "analysis": {{
    "strengths": "...",
    "weaknesses": "...",
    "dislikes": "...",
    "suggestions": "..."
  }}
}}

Resume:
{resume_text}
'''

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
    app.run(debug=True)
