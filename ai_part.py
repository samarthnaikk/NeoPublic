import google.generativeai as genai
from dotenv import load_dotenv
import os
load_dotenv()
gem_api_key = os.environ.get('gem_api_key')
genai.configure(api_key=gem_api_key)
model = genai.GenerativeModel("gemini-2.5-pro")

def get_ans(question: str) -> str:
    prompt = f"""You are a code generator.
Given the following question, generate a Java program that answers it.
Only return the code in this format:

class Ex {{
public static void main(String[] args) {{
    // the main code here
}}
}}

Do not include any comments, explanations, or extra output.
The question is: {question}
"""
    response = model.generate_content(prompt)
    response = response.text.split('```')

    return response[-2][4:] if response[-2].startswith('java') else response[-2].strip()
