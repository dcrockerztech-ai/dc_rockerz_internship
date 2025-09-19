# app.py
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import csv, os
from logic import recommend

# point Flask to Frontend folder for templates
FRONTEND_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Frontend"))
app = Flask(__name__, template_folder=FRONTEND_FOLDER)
CORS(app)

# robust path to dataset
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "internship.csv"))

# fail-fast check
if not os.path.isfile(DATA_PATH):
    print("ERROR: data file not found at:", DATA_PATH)
    import sys; sys.exit(1)

# load internships
def load_internships():
    internships = []
    with open(DATA_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            internships.append(r)
    return internships

INTERN = load_internships()

# health check
@app.route('/health')
def health():
    return jsonify({"status": "ok", "count": len(INTERN)})

# recommend endpoint
@app.route('/recommend', methods=['POST'])
def recommend_api():
    payload = request.json or {}
    results = recommend(payload, INTERN, top_k=5)
    return jsonify({"results": results})

# sample endpoint
import random
@app.route('/sample')
def sample():
    sample_jobs = random.sample(INTERN, min(5, len(INTERN)))
    return jsonify({
        "results": [
            {
                "id": j.get("id"),
                "title": j.get("title"),
                "company": j.get("company"),
                "location": j.get("location"),
                "skills": j.get("skills"),
                "tags": j.get("tags"),
                "stipend": j.get("stipend")
            }
            for j in sample_jobs
        ]
    })

# serve frontend
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/finder.html')
def finder():
    return render_template('finder.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(FRONTEND_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
