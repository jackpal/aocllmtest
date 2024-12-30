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
  
  # Heuristic for slightly incorrect code block markdown.
  def replace_func(match):
        return "\n```" + match.group(1)

  # Use a single regular expression to find and replace
  markdown_text = re.sub(r"```(\s*)$", replace_func, markdown_text)
  
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

  return markdown_text

if __name__ == "__main__":
  print(extract_solve_function("""```python
import sys
from itertools import combinations

weapons = {
    'Dagger': (8, 4, 0),
    'Shortsword': (10, 5, 0),
    'Warhammer': (25, 6, 0),
    'Longsword': (40, 7, 0),
    'Greataxe': (74, 8, 0)
}

armor = {
    'None': (0, 0, 0),
    'Leather': (13, 0, 1),
    'Chainmail': (31, 0, 2),
    'Splintmail': (53, 0, 3),
    'Bandedmail': (75, 0, 4),
    'Platemail': (102, 0, 5)
}

rings = {
    'None1': (0, 0, 0),
    'None2': (0, 0, 0),
    'Damage +1': (25, 1, 0),
    'Damage +2': (50, 2, 0),
    'Damage +3': (100, 3, 0),
    'Defense +1': (20, 0, 1),
    'Defense +2': (40, 0, 2),
    'Defense +3': (80, 0, 3)
}

def fight(player_hp, player_damage, player_armor, boss_hp, boss_damage, boss_armor):
  while True:
    boss_hp -= max(1, player_damage - boss_armor)
    if boss_hp <= 0:
      return 'Player'
    player_hp -= max(1, boss_damage - player_armor)
    if player_hp <= 0:
      return 'Boss'

def min_cost(boss_stats):
  min_gold = float('inf')
  for w in weapons.values():
    for a in armor.values():
      for r1, r2 in combinations(rings.values(), 2):
        player_damage = w[1] + r1[1] + r2[1]
        player_armor = w[2] + a[2] + r1[2] + r2[2]

        cost = w[0] + a[0] + r1[0] + r2[0]

        if fight(100, player_damage, player_armor, *boss_stats) == 'Player':
          min_gold = min(min_gold, cost)
  return min_gold

boss_stats = [int(x.strip()) for x in sys.stdin.read().split(':')[1].split('\n')]
print(min_cost(boss_stats))```"""))
