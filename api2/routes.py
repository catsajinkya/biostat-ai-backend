from flask import Blueprint, request, jsonify
from .prompt import summarize_history

api2_bp = Blueprint("api2", __name__)  
@api2_bp.route("/summarize_history", methods=["POST"])
def summarize():
    report_json = request.get_json()
    if not report_json:
        return jsonify({"error": "No report data provided"}), 400

    summary = summarize_history(report_json)
    return jsonify({"summary": summary})



