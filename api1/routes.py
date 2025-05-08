from flask import Blueprint, request, jsonify
from .prompt import summarize_report
import json
import google.generativeai as genai
from flask import Blueprint
import io
import PyPDF2
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image
import base64

ApiRouter = Blueprint('report-generator', __name__)

api1_bp = Blueprint("api1", __name__)  
@api1_bp.route("/summarize_report", methods=["POST"])
def summarize():
    report_json = request.get_json()
    if not report_json:
        return jsonify({"error": "No report data provided"}), 400
    print("report_json ",report_json)
    summary = summarize_report(report_json)
    return jsonify({"summary": summary})



def build_prompt_data_extraction():
    prompt = """You are an expert at extracting information from medical lab report images and structuring it as JSON. Analyze the provided image and extract the following information, formatting it as a JSON object with the following structure:

{
  "report_details": {
    "report_name": "string (name or title of the report, infer from context if not explicitly stated)",
    "report_date": "string (format: DD-MMM-YY)",
    "lab_name": "string",
    "lab_id": "string",
    "lab_location": "string",
    "lab_contact_number": "string",
  },
  "tests": [
    {
      "test_name": "string",
      "interpretation": "string (a brief overall interpretation of this test, if possible, otherwise null)",
      "components": [
        {
          "test_component_name": "string",
          "result_value": "string",
          "units": "string (may be null if not provided)",
          "reference_range": {
            "min": "string (minimum normal value, may be null)",
            "max": "string (maximum normal value, may be null)"
          }
          
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


def call_gemini_with_image(prompt, image_data, mime_type="image/jpeg"):
    model = genai.GenerativeModel("gemini-2.0-flash")
    image = {"mime_type": mime_type, "data": image_data}
    response = model.generate_content([prompt, image])
    return response.text

@ApiRouter.route("/api/extract_report_data", methods=["POST"])
def extract_report_from_file():
    print(f"Received Content-Type (File): {request.files['file'].content_type}")
    print(f"Received Headers: {request.headers}")
    # ALLOWED_TYPES = {'image/jpeg', 'image/png', 'application/pdf'}
    
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    # if file.content_type.lower() not in {t.lower() for t in ALLOWED_TYPES}:
    #     return jsonify({"error": "Unsupported file type. Allowed: JPEG, PNG, PDF"}), 400

    try:
        prompt = build_prompt_data_extraction()
        
        if file.content_type == 'application/pdf':
            pdf_bytes = file.read()
            images = convert_from_bytes(pdf_bytes, dpi=300, first_page=1, last_page=1)
            if images:
                image_buffer = io.BytesIO()
                images[0].save(image_buffer, format="JPEG") 
                mime_type = "image/jpeg" 
                image_data = image_buffer.getvalue()
                extracted_json_string = call_gemini_with_image(prompt, image_data, mime_type)
        else:
            image_data = file.read()
            mime_type = file.content_type
            extracted_json_string = call_gemini_with_image(prompt, image_data, mime_type)

        # Clean and parse JSON response
        extracted_json_string = extracted_json_string.strip()
        extracted_json_string = extracted_json_string.removeprefix("```json").removesuffix("```").strip()
        extracted_data = json.loads(extracted_json_string)
        
        return jsonify(extracted_data)
        
    except json.JSONDecodeError as e:
        return jsonify({"error": "Failed to parse Gemini output", "raw_output": extracted_json_string}), 500
    except Exception as e:
        return jsonify({"error": f"Processing error: {str(e)}"}), 500
    
def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extracts text from a PDF file (text-based or scanned/image-based using OCR).
    
    Args:
        pdf_bytes (bytes): Raw PDF file data.
    
    Returns:
        str: Extracted text.
    
    Raises:
        ValueError: If PDF is empty or cannot be processed.
    """
    text = ""
    
    # Try extracting text directly (works for text-based PDFs)
    try:
        with io.BytesIO(pdf_bytes) as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        
        # If sufficient text was extracted, return it
        if len(text.strip()) > 50:  # Arbitrary threshold
            return text.strip()
    
    except Exception as e:
        print(f"Standard PDF extraction failed (likely scanned PDF): {e}")
    
    # Fallback to OCR for scanned/image-based PDFs
    try:
        images = convert_from_bytes(pdf_bytes, dpi=300)  # Higher DPI = better OCR accuracy
        for img in images:
            text += pytesseract.image_to_string(img) + "\n"
        return text.strip()
    
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF (neither text nor OCR worked): {e}")

