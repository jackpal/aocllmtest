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
    return ('success', text)
