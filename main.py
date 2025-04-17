from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import json

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
            return jsonify({"error": "No resume file uploaded"}), 400

        resume_file = request.files["resume"]
        resume_text = resume_file.read().decode("utf-8")

        prompt = f"""
You are a resume expert AI. Read the resume below and return only valid JSON in this format:

{{
  "score": 0 to 100 (based on formatting, keyword usage, ATS compatibility),
  "badge": "Not Recruiter-Friendly" or "Almost There" or "Impressive Resume" or "ATS Optimized",
  "analysis": {{
    "strengths": "List 2-3 key strengths",
    "weaknesses": "List 2-3 key weaknesses",
    "dislikes": "What might recruiters dislike?",
    "suggestions": "3 solid improvement tips"
  }}
}}

ONLY return valid JSON. No explanations. Resume:
"""{resume_text}"""
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            temperature=0.7,
            messages=[
                {"role": "system", "content": "You are a resume reviewing assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        content = response.choices[0].message.content.strip()

        try:
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()

            data = json.loads(content)

            required_keys = {"score", "badge", "analysis"}
            if not all(key in data for key in required_keys):
                raise ValueError("Missing keys in response")

            return jsonify(data)

        except Exception as parse_err:
            return jsonify({
                "error": "Failed to parse GPT response",
                "raw_response": content
            }), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

