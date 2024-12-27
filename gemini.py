import google.generativeai as genai
import keyring
import re
from typing import Tuple

def generate(model_name : str, prompt: str) -> Tuple[str, str]:
    genai.configure(api_key=keyring.get_password("aocllm", "google-ai-studio"))
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    text = response.text
    result = extract_solve_function(text)
    if result:
        return ('success', result)
    return ('failure', text)


def extract_solve_function(markdown_text: str) -> str | None:
  """
  Extracts the contents of the last Python code block that defines a "solve" function from a Markdown string.

  If there are no code blocks, it checks if the input contains a definition of a solve function, and if so, 
  returns the whole input.

  Args:
    markdown_text: The input string in Markdown format.

  Returns:
    The contents of the last Python code block defining a "solve" function, 
    or the whole input if no code blocks are found but a solve function definition exists,
    or None if no solve function is found.
  """
  code_blocks: list[str] = re.findall(r"```python\n(.*?)\n```", markdown_text, re.DOTALL)
  solve_function_code: str | None = None

  for block in reversed(code_blocks):  # Iterate in reverse to find the last one
    if re.search(r"^def\s+solve\s*\(", block, re.MULTILINE):
      solve_function_code = block
      break
  
  if solve_function_code is None and not code_blocks:
    if re.search(r"^def\s+solve\s*\(", markdown_text, re.MULTILINE):
      solve_function_code = markdown_text

  return solve_function_code