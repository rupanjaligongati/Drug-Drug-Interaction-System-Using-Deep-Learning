
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load env from backend/.env
backend_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(backend_dir, ".env")
load_dotenv(dotenv_path)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    # Explicit backup
    load_dotenv() 
    api_key = os.getenv("GEMINI_API_KEY")

print(f"Key loaded: {'Yes' if api_key else 'No'}")

if api_key:
    genai.configure(api_key=api_key)
    try:
        print("Listing models...")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")
