const API_URL = "http://127.0.0.1:5000";

function splitInput(val) {
  return val.split(",").map(v => v.trim().toLowerCase()).filter(Boolean);
}

async function analyze() {
  const btn = document.getElementById("analyzeBtn");
  btn.textContent = "Analyzing...";
  btn.disabled = true;

  const payload = {
    age: parseInt(document.getElementById("age").value) || 0,
    gender: document.getElementById("gender").value,
    disease: document.getElementById("disease").value.trim().toLowerCase(),
    current_meds: splitInput(document.getElementById("current_meds").value),
    recent_meds: splitInput(document.getElementById("recent_meds").value),
    allergies: splitInput(document.getElementById("allergies").value),
    symptoms: splitInput(document.getElementById("symptoms").value)
  };

  if (!payload.current_meds.length) {
    alert("Please enter at least one current medication.");
    btn.textContent = "Analyze Medications";
    btn.disabled = false;
    return;
  }

  try {
    const res = await fetch(`${API_URL}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (!data.success) {
      alert("Error: " + (data.error || "Unknown error"));
      return;
    }

    renderResults(data.results);

  } catch (err) {
    alert("Could not connect to backend. Make sure app.py is running on port 5000.");
    console.error(err);
  } finally {
    btn.textContent = "Analyze Medications";
    btn.disabled = false;
  }
}

function renderResults(results) {
  const section = document.getElementById("results");
  const container = document.getElementById("result-cards");

  section.classList.remove("hidden");
  container.innerHTML = "";

  results.forEach(r => {
    const riskClass = {
      "HIGH": "risk-high",
      "MODERATE": "risk-moderate",
      "LOW": "risk-low",
      "SAFE": "risk-safe",
      "UNKNOWN": "risk-unknown"
    }[r.risk_level] || "";

    const issueHTML = r.issues.map(issue => {
      const type = issue.type || "info";
      const msg = issue.message || issue;
      const icons = { allergy: "🚨", interaction: "💊", side_effect: "⚠️", contraindication: "🚫" };
      return `<div class="issue issue-${type}">${icons[type] || "•"} ${msg}</div>`;
    }).join("");

    const altHTML = r.alternatives && r.alternatives.length
      ? `<div class="alternatives">Possible alternatives to discuss with doctor: <strong>${r.alternatives.join(", ")}</strong></div>`
      : "";

    container.innerHTML += `
      <div class="result-card ${riskClass}">
        <div class="card-header">
          <div>
            <span class="drug-name">${r.drug.toUpperCase()}</span>
            <span class="drug-class">${r.drug_class}</span>
          </div>
          <div class="risk-badge ${riskClass}">${r.risk_level} RISK</div>
        </div>
        <div class="score-bar">
          <div class="score-fill" style="width: ${Math.min(r.score, 100)}%"></div>
          <span class="score-label">Risk Score: ${r.score}</span>
        </div>
        ${issueHTML || '<div class="issue">✅ No issues detected</div>'}
        ${altHTML}
      </div>
    `;
  });

  section.scrollIntoView({ behavior: "smooth" });
}
