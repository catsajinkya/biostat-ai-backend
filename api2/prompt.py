from .gemini_utils import call_gemini
import json

def summarize_history(report_data):
    return f"""
You are a medical assistant. Analyze the patient’s complete medical history and current reports below and generate an overall health summary. 
Include health conditions, risk factors, improvements, and anything that needs attention.
- Use plain English.
- Do NOT use Markdown or special formatting.
- Highlight diagnosis, abnormal results, lab names, and suggestions.
- Ignore internal codes unless medically relevant.



JSON:
{json.dumps(report_data, indent=2)}
"""

    summary = call_gemini(prompt)
    return summary.strip()
