import google.generativeai as genai
import os

# Set your Gemini API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.0-flash")

def call_gemini(prompt: str) -> str:
    response = model.generate_content(prompt)
    return response.text.strip()
