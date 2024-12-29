import re

def extract_solve_function(markdown_text: str) -> str | None:
  """
  Extracts the contents of the last Python code block from a Markdown string.

  If there are no code blocks, it checks if the input contains a definition of a solve function, and if so, 
  returns the whole input.

  Args:
    markdown_text: The input string in Markdown format.

  Returns:
    The contents of the last Python code block, 
    or the whole input if no code blocks are found.
  """
  code_blocks: list[str] = re.findall(r"```python\n(.*?)\n```", markdown_text, re.DOTALL)
  
  if code_blocks:
    return code_blocks[-1] + '\n'

  return markdown_text