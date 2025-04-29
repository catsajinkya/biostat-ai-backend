from flask import request, jsonify
import requests
from .gemini_utils import call_gemini
from .prompt import build_prompt_from_report
import json
import google.generativeai as genai
from flask import Blueprint

ApiRouter = Blueprint('report-generator', __name__)

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



def build_prompt_for_image_extraction():
    prompt = """You are an expert at extracting information from medical lab report images and structuring it as JSON. Analyze the provided image and extract the following information, formatting it as a JSON object with the following structure:

{
  "report_details": {
    "report_date": "string (format: DD-MM-YYYY)",
    "lab_name": "string",
    "lab_id": "string",
    "lab_location": "string",
    "lab_contact_number": "string"
  },
  "tests": [
    {
      "test_name": "string",
      "interpretation": "string (a brief overall interpretation of this test, if possible, otherwise null)",
      "components": [
        {
          "test_component_name": "string",
          "result_value": "string",
          "units": "string (may be null if not provided)"
        }
        // ... more components
      ]
    }
    // ... more tests
  ],
  "raw_text": "string (the complete text content of the report)"
}
For each test, look for any specific 'interpretation', 'note', or 'comment' that is explicitly mentioned for that entire test within the report. If such a statement exists, extract it verbatim and set it as the 'interpretation' for that test. If no such explicit interpretation or note is found for the test, set the 'interpretation' to null.
Ensure that all extracted values are strings. If a value is not explicitly present, use null or an empty string as appropriate. Do not add any extra commentary or explanations in the JSON output. Just provide the JSON.
"""
    return prompt

def call_gemini_with_image(prompt, image_data):
    model = genai.GenerativeModel("gemini-2.0-flash")
    image = {"mime_type": "image/jpeg", "data": image_data} 
    response = model.generate_content([prompt, image])
    return response.text

@ApiRouter.route("/api/extract_report_data", methods=["POST"])
def extract_report_from_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({"error": "No image selected"}), 400
    if image_file:
        try:
            image_data = image_file.read()
            prompt = build_prompt_for_image_extraction()
            extracted_json_string = call_gemini_with_image(prompt, image_data)
            if extracted_json_string.startswith("```json"):
                extracted_json_string = extracted_json_string[7:]
            if extracted_json_string.endswith("```"):
                extracted_json_string = extracted_json_string[:-3]

            extracted_json_string = extracted_json_string.strip()

            extracted_data = json.loads(extracted_json_string)
            return jsonify(extracted_data)
        except json.JSONDecodeError as e:
            return jsonify({"error": f"Failed to decode Gemini output as JSON: {e}", "gemini_output": extracted_json_string}), 500
        except Exception as e:
            return jsonify({"error": f"Error processing image or Gemini call: {e}"}), 500
    return jsonify({"error": "Invalid image file"}), 400
