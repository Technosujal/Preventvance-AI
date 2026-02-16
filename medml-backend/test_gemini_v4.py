import os
import google.generativeai as genai
from dotenv import load_dotenv
import traceback
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

with open('gemini_diagnostics_2.txt', 'w', encoding='utf-8') as f:
    api_key = os.getenv('GEMINI_API_KEY')
    genai.configure(api_key=api_key)
    
    models_to_test = ['gemini-2.0-flash', 'gemini-2.0-flash-lite', 'gemini-flash-latest']
    
    for m_name in models_to_test:
        f.write(f"\n--- Testing {m_name} ---\n")
        try:
            model = genai.GenerativeModel(m_name)
            response = model.generate_content("Ping")
            f.write(f"SUCCESS: {response.text}\n")
        except Exception as e:
            f.write(f"FAILED: {e}\n")
        time.sleep(1) # avoid creating rate limits
