import os
import google.generativeai as genai
from dotenv import load_dotenv
import traceback

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
print(f"API Key present: {bool(api_key)}")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        print("\nListing available models:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
        
        print("\nAttempting generation with gemini-1.5-flash:")
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Ping")
        print(f"Response: {response.text}")
        
    except Exception:
        print("\nERROR OCCURRED:")
        traceback.print_exc()
else:
    print("No API Key found")
