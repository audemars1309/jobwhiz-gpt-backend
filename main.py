from flask import Flask, request, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "JobWhiz GPT Resume Analyzer is running!"

@app.route('/analyze', methods=['POST'])
def analyze_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'No resume file uploaded'}), 400

    resume = request.files['resume']
    content = resume.read().decode('utf-8', errors='ignore')

    score = random.randint(50, 95)

    if score < 60:
        badge = "Not Recruiter-Friendly"
    elif score < 80:
        badge = "Almost There"
    else:
        badge = "Impressive Resume"

    analysis = {
        "strengths": "Strong formatting, clear sections, good language.",
        "weaknesses": "Needs more metrics, lacks achievements.",
        "dislikes": "Too many buzzwords, unclear objective.",
        "suggestions": "Use numbers, reduce fluff, add specific results."
    }

    return jsonify({
        "score": score,
        "badge": badge,
        "analysis": analysis
    })

if _name_ == '__main__':
    app.run(host='0.0.0.0', port=10000)
