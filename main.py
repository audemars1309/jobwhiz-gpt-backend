from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "JobWhizAI GPT Resume Backend is running!"

@app.route('/analyze', methods=['POST'])
def analyze():
    resume = request.json.get('resume')
    if not resume:
        return jsonify({"error": "No resume provided"}), 400

    # Fake score logic (replace with real AI later)
    return jsonify({
        "score": 62,
        "badge": "Not Recruiter-Friendly"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
