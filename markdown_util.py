import markdown
from bs4 import BeautifulSoup
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
    
  md_html = markdown.markdown(markdown_text, extensions=['fenced_code'])
  soup = BeautifulSoup(md_html,features="html.parser")
  code_blocks = soup.find_all('code', {'class':'language-python'})
  
  if code_blocks:
    last_code_block = code_blocks[-1]
    last_code_block_text = last_code_block.text
    if "```python" in last_code_block_text:
      # Parsing failed, return original text.
      return markdown_text
    return last_code_block_text

  # Heuristic for slightly incorrect code block markdown.
  pattern = r"```python\n(.*?)\n?```"  # Regex to find Python code blocks
  matches = re.findall(pattern, markdown_text, re.DOTALL)
  if matches:
    return matches[-1]
  
  # Give up, return original text.
  return markdown_text

if __name__ == "__main__":
  print(extract_solve_function("""```python
import sys
from collections import defaultdict

def is_safe(state):
    for f in range(4):
        if state[f]['G']:
            for m in state[f]['M']:
                if m != state[f]['G'][0]:  
                    return False
    return True

def hash_state(state):
    return tuple((tuple(sorted(items)),) for items in [state[f]['M'], state[f]['G']] for f in range(4)])

def solve():
    lines = sys.stdin.readlines()
    floors = defaultdict(lambda: {'M': [], 'G': []})
    for i, line in enumerate(lines):
        if 'a' in line:
            floors[i // 3]['G'].append('H')
        elif 'b' in line:
            floors[i // 3]['G'].append('L')

    for i, line in enumerate(lines):
        for c in line.strip():
            if c.isupper() and c != 'E':
                floors[i // 3]['M'].append(c)

    queue = [(floors, 0)]
    visited = set([hash_state(floors)])

    while queue:
        state, steps = queue.pop(0)
        if all(item for floor in state.values() for item in floor.values()):
            return steps

        for f in range(4):
            if 'E' in floors[f]:
                current_floor = f
                break

        for mf in range(max(0, current_floor - 1), min(3, current_floor + 1) + 1):
            for item_type in ['M', 'G']:
                items = state[current_floor][item_type]
                for item in items:

                    new_state = [dict(floor) for floor in state]
                    new_state[mf][item_type].append(item)
                    new_state[current_floor][item_type].remove(item)

                    if is_safe(new_state):

                        hashed_state = hash_state(new_state)

                        if hashed_state not in visited:
                            queue.append((new_state, steps + 1))
                            visited.add(hashed_state)

    return -1

print(solve())```



"""))
