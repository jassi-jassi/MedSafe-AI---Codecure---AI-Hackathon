from flask import Flask, request, jsonify
from flask_cors import CORS
from ai_engine import analyze_patient

app = Flask(__name__)
CORS(app)  # Allow frontend requests

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "MedSafe AI is running"})

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        required = ["current_meds", "symptoms"]
        for field in required:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        results = analyze_patient(data)

        return jsonify({
            "success": True,
            "total_drugs_analyzed": len(results),
            "results": results
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/drugs", methods=["GET"])
def list_drugs():
    """Return list of all drugs in database."""
    import json, os
    with open(os.path.join(os.path.dirname(__file__), "data.json")) as f:
        db = json.load(f)
    return jsonify({"drugs": list(db["drugs"].keys())})

if __name__ == "__main__":
    print("MedSafe AI Backend starting on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
