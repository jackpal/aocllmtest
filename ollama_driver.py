import markdown_util
import ollama
from typing import List, Tuple

def models() -> List[str]:
    return [
        'gemma2:2b',
        'gemma2:9b',
        'gemma2:27b',
        'llama3.3',
        'qwen2.5-coder:32b',
        ]

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

if __name__ == "__main__":
    for model in models():
        print(model, generate(model, 'what LLM model are you?'))
