import markdown_util
import ollama
from typing import Tuple

def generate(model_name : str, prompt: str) -> Tuple[str, str]:
    response = ollama.chat(
        model_name, 
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    text = response.message.content
    result = markdown_util.extract_solve_function(text)
    if result:
        return ('success', result)
    return ('failure', text)

def model_quota_timeout(model_name: str) -> int:
    return 10
