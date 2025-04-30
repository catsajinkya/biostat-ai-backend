from flask import Blueprint, request, jsonify
from .prompt import summarize_report

api1_bp = Blueprint("api1", __name__)  # 👈 this will be imported in __init__.py

@api1_bp.route("/summarize_report", methods=["POST"])
def summarize():
    report_json = request.get_json()
    if not report_json:
        return jsonify({"error": "No report data provided"}), 400

    summary = summarize_report(report_json)
    return jsonify({"summary": summary})
