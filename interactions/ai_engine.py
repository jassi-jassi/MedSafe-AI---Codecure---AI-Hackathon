import json
import os

# Load dataset from same directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data.json")

with open(DATA_PATH, "r") as f:
    database = json.load(f)["drugs"]

# Scoring weights
SEVERITY_WEIGHTS = {"mild": 10, "moderate": 25, "severe": 50}
INTERACTION_WEIGHTS = {"low": 10, "moderate": 20, "high": 40}

def normalize(items):
    """Lowercase + strip all items in a list."""
    return [item.strip().lower() for item in items if item.strip()]

def analyze_patient(data):
    age = data.get("age", 0)
    gender = data.get("gender", "unknown")
    disease = data.get("disease", "").lower()
    current_meds = normalize(data.get("current_meds", []))
    recent_meds = normalize(data.get("recent_meds", []))
    allergies = normalize(data.get("allergies", []))
    symptoms = normalize(data.get("symptoms", []))

    results = []

    for drug in current_meds:
        if drug not in database:
            results.append({
                "drug": drug,
                "score": 0,
                "issues": ["Drug not found in database — verify spelling"],
                "risk_level": "UNKNOWN",
                "drug_class": "Unknown",
                "alternatives": []
            })
            continue

        info = database[drug]
        score = 0
        issues = []

        # 1. Side effect matching
        for se in info["side_effects"]:
            if se["effect"] in symptoms:
                points = SEVERITY_WEIGHTS[se["severity"]]
                score += points
                issues.append({
                    "type": "side_effect",
                    "message": f"Side effect detected: {se['effect']} ({se['severity']})",
                    "points": points
                })

        # 2. Allergy check
        for allergy in allergies:
            if allergy in info["allergies"]:
                score += 60
                issues.append({
                    "type": "allergy",
                    "message": f"Allergy risk: {allergy} — HIGH RISK",
                    "points": 60
                })

        # 3. Drug-drug interaction check (current + recent 24h)
        all_other_drugs = [d for d in current_meds if d != drug] + recent_meds
        for interaction in info["interactions"]:
            if interaction["drug"] in all_other_drugs:
                points = INTERACTION_WEIGHTS[interaction["risk"]]
                score += points
                issues.append({
                    "type": "interaction",
                    "message": f"Interaction with {interaction['drug']} ({interaction['risk']} risk)",
                    "points": points
                })

        # 4. Contraindication check
        for condition in info["contraindications"]:
            if condition.lower() in disease:
                score += 40
                issues.append({
                    "type": "contraindication",
                    "message": f"Contraindicated for: {condition}",
                    "points": 40
                })

        # Risk level classification
        if score >= 80:
            risk = "HIGH"
        elif score >= 40:
            risk = "MODERATE"
        elif score > 0:
            risk = "LOW"
        else:
            risk = "SAFE"

        # Suggest alternatives (other drugs in DB with same use)
        alternatives = []
        for d_name, d_info in database.items():
            if d_name == drug:
                continue
            shared_uses = set(d_info["uses"]) & set(info["uses"])
            if shared_uses and d_name not in current_meds:
                alternatives.append(d_name)

        results.append({
            "drug": drug,
            "score": score,
            "issues": issues,
            "risk_level": risk,
            "drug_class": info["class"],
            "alternatives": alternatives[:3]
        })

    return sorted(results, key=lambda x: x["score"], reverse=True)


def generate_summary(results):
    """Generate a human-readable summary."""
    if not results:
        return "No medications analyzed."

    lines = []
    for r in results:
        lines.append(f"\n{'='*50}")
        lines.append(f"Drug: {r['drug'].upper()} | Class: {r['drug_class']}")
        lines.append(f"Risk Score: {r['score']} | Risk Level: {r['risk_level']}")

        if r["issues"]:
            lines.append("\nIssues Found:")
            for issue in r["issues"]:
                if isinstance(issue, dict):
                    lines.append(f"  [{issue['type'].upper()}] {issue['message']}")
                else:
                    lines.append(f"  {issue}")
        else:
            lines.append("No issues detected for this drug.")

        if r.get("alternatives"):
            lines.append(f"\nPossible alternatives to discuss with doctor: {', '.join(r['alternatives'])}")

        lines.append("\nDISCLAIMER: Consult your doctor before making any changes.")

    return "\n".join(lines)


# ---- For Jupyter Notebook use ----
if __name__ == "__main__":
    sample_input = {
        "age": 28,
        "gender": "female",
        "disease": "fever and kidney disease",
        "current_meds": ["ibuprofen", "amoxicillin", "paracetamol"],
        "recent_meds": ["aspirin"],
        "allergies": ["penicillin"],
        "symptoms": ["rash", "stomach pain", "nausea"]
    }

    results = analyze_patient(sample_input)
    print(generate_summary(results))
