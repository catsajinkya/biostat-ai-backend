import json

def build_prompt_from_report(report_data: dict) -> str:
    return f"""
You are a medical assistant. Analyze the patient’s complete medical history and current reports below and generate an overall health summary. 
Include health conditions, risk factors, improvements, and anything that needs attention.


Report JSON:
{json.dumps(report_data, indent=2)}
"""
