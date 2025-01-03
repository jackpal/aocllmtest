import google.generativeai as genai
import keyring
import markdown_util
from typing import List, Tuple

def models() -> List[str]:
    return [
        'gemini-exp-1206',
        'gemini-2.0-flash-exp',
        'gemini-2.0-flash-thinking-exp-1219',
        'gemini-1.5-pro',
        'gemini-1.5-flash',
        'gemini-1.5-flash-8b',
        ]

genai.configure(api_key=keyring.get_password("aocllm", "google-ai-studio"))

_model_dict = dict()    

def generate(model_name : str, prompt: str) -> Tuple[str, str]:
    global _configured
    global _model_dict
    if model_name not in _model_dict:
        _model_dict[model_name] = genai.GenerativeModel(model_name)
    model = _model_dict[model_name]
    try:
        response = model.generate_content(prompt)
    except Exception as e:
        exception_str = str(e)
        if "429" in exception_str or "500" in exception_str:
            # Assume it's a quota issue.
            return ('quota', exception_str)
        else:
            return ('error', exception_str)
    try:
        text = response.text
    except Exception as e:
        exception_str = str(e)
        return ('error', 'response.text ' + exception_str)
    result = markdown_util.extract_solve_function(text)
    if result:
        return ('success', result)
    return ('failure', text)


def model_quota_timeout(model_name: str) -> int:
    if model_name in ['gemini-exp-1206', 'gemini-1.5-pro']:
        # The quota is 50 calls per day
        return 24*3600/50
    else:
        # 1500 calls per day but 10 RPM. We don't know which quota we exhausted,
        # assume it's the longer one.
        return max(24*3600/1500, 60/10)

if __name__ == "__main__":
    for m in genai.list_models():
        if "generateContent" in m.supported_generation_methods:
            print(m)
    # for model in models():
    #     print(model, generate(model, 'what Gemini model are you?'))
