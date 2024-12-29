import google.generativeai as genai
import keyring
import markdown_util
from typing import Tuple

def generate(model_name : str, prompt: str) -> Tuple[str, str]:
    genai.configure(api_key=keyring.get_password("aocllm", "google-ai-studio"))
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    text = response.text
    result = markdown_util.extract_solve_function(text)
    if result:
        return ('success', result)
    return ('failure', text)


