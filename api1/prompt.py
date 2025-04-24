import json

def build_prompt_from_report(report_data: dict) -> str:
    return f"""
You are a medical assistant. Summarize the following medical report for a patient in simple, clear language.
 Include key health information, diagnosis, test results, and any recommendations or next steps.

Report JSON:
{json.dumps(report_data, indent=2)}
"""
