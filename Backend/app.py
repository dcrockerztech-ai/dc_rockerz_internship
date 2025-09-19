import os
import json
import csv
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from logic import recommend

# Flask setup with templates folder
TEMPLATE_FOLDER = os.path.join(os.path.dirname(__file__), "templates")
app = Flask(__name__, template_folder=TEMPLATE_FOLDER)
CORS(app)

# Dataset path
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "Data", "internships.csv")

# Load dataset
INTERN = []
with open(DATA_PATH, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        INTERN.append({
            "id": row.get("id", ""),
            "title": row.get("title", ""),
            "company": row.get("company", ""),
            "location": row.get("location", ""),
            "skills": row.get("skills", ""),
            "stipend": row.get("stipend", ""),
        })


# ---------------- Routes ---------------- #

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/finder")
def finder():
    return render_template("finder.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok", "count": len(INTERN)})


@app.route("/sample")
def sample():
    return jsonify(INTERN[:5])


@app.route("/recommend", methods=["POST"])
def recommend_api():
    try:
        payload = request.get_json(force=True)

        # Normalize: ensure skills are string (not list)
        if isinstance(payload.get("skills"), list):
            payload["skills"] = ",".join(payload["skills"])

        results = recommend(payload, INTERN, top_k=5)
        return jsonify({"results": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # For local dev only; Render will use gunicorn
    app.run(host="0.0.0.0", port=5000, debug=True)
