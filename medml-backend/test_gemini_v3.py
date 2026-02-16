import os
import google.generativeai as genai
from dotenv import load_dotenv
import traceback
import sys

# Force utf-8 for stdout/stderr
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

with open('gemini_diagnostics.txt', 'w', encoding='utf-8') as f:
    api_key = os.getenv('GEMINI_API_KEY')
    f.write(f"API Key present: {bool(api_key)}\n")
    
    if api_key:
        try:
            genai.configure(api_key=api_key)
            
            f.write("\nListing available models:\n")
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    f.write(f"- {m.name}\n")
            
            f.write("\nAttempting generation with gemini-1.5-flash:\n")
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content("Ping")
                f.write(f"Response: {response.text}\n")
            except Exception as e:
                f.write(f"Error with gemini-1.5-flash: {e}\n")
                
            f.write("\nAttempting generation with gemini-pro:\n")
            try:
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content("Ping")
                f.write(f"Response: {response.text}\n")
            except Exception as e:
                f.write(f"Error with gemini-pro: {e}\n")

        except Exception:
            f.write("\nFATAL ERROR:\n")
            traceback.print_exc(file=f)
    else:
        f.write("No API Key found\n")
