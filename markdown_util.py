import markdown
from bs4 import BeautifulSoup

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
    if "'''python" in last_code_block_text:
      # Parsing failed, return original text.
      return markdown_text
    return last_code_block_text

  return markdown_text

if __name__ == "__main__":
  print(extract_solve_function("""```python
import sys

def p(s, t, p2):
  for i, l in enumerate(s):
    ok = True
    for k, v in l.items():
      if p2 and (k == 'cats' or k == 'trees'):
        if v <= t[k]:
          ok = False
          break
      elif p2 and (k == 'pomeranians' or k == 'goldfish'):
        if v >= t[k]:
          ok = False
          break
      elif v != t[k]:
        ok = False
        break
    if ok:
      return i + 1

s = []
for l in sys.stdin:
  l = l.strip().split(' ')
  d = {}
  for j in range(2, len(l), 2):
    k = l[j].replace(':', '')
    v = int(l[j + 1].replace(',', ''))
    d[k] = v
  s.append(d)
t = {
    'children': 3,
    'cats': 7,
    'samoyeds': 2,
    'pomeranians': 3,
    'akitas': 0,
    'vizslas': 0,
    'goldfish': 5,
    'trees': 3,
    'cars': 2,
    'perfumes': 1,
}
p2 = sys.argv[1] == '2'
print(p(s, t, p2))
```"""))
