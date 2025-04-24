from flask import request, jsonify
import requests
from .gemini_utils import call_gemini
from .prompt import build_prompt_from_report

POSTMAN_API_URL = "https://00134b5e-9ba9-48fc-a53d-ba98849cd2e0.mock.pstmn.io/v1/api/patient/diagnostic-report"

def summarize_report():
    data = request.json
    if not data or "patient_id" not in data:
        return jsonify({"error": "Missing patient_id"}), 400

    try:
        response = requests.get(f"{POSTMAN_API_URL}?patient_id={data['patient_id']}")
        response.raise_for_status()
        report_data = response.json()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

    prompt = build_prompt_from_report(report_data)
    summary = call_gemini(prompt)

    return jsonify({"summary": summary})
