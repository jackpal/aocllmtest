import google.generativeai as genai
import keyring

def generate(model_name, prompt):
    genai.configure(api_key=keyring.get_password("aocllm", "google-ai-studio"))
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    text = response.text
    python_header = "```python\n"
    python_footer = "\n```"
    parts = text.split(python_header)
    if len(parts) > 1:
        text = parts[1]
    parts = text.split(python_footer)
    if len(parts) > 1:
        text = parts[0]
    return text
