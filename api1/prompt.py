from .gemini_utils import call_gemini
import json

def summarize_report(report_data):
    prompt = f"""
You are an experienced medical assistant. Given the following diagnostic report JSON, generate a clear and concise **summary** with **actionable health insights** for the doctor and patient.

- Use plain English.
- Do NOT use Markdown or special formatting.
- Highlight diagnosis, abnormal results, lab names, and suggestions.
- Ignore internal codes unless medically relevant.

JSON:
{json.dumps(report_data, indent=2)}
"""

    summary = call_gemini(prompt)
    return summary.strip()
