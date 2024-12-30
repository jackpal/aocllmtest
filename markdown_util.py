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
  
  soup = BeautifulSoup(markdown.markdown(markdown_text),features="html.parser")
  code_blocks = soup.find_all('code')
  
  if code_blocks:
    last_code_block = code_blocks[-1].text
    return last_code_block

  return markdown_text

if __name__ == "__main__":
  print(extract_solve_function("""I need to write a Python program to solve the "Wizard Simulator 20XX" puzzle, specifically Part 2.
The program should take the puzzle part ('2') as a command-line argument.
The core of the problem is a turn-based combat simulation with spells and effects.
I need to find the minimum mana spent to win the fight. This suggests a search algorithm, potentially a breadth-first search or a depth-first search with pruning.
The state of the game includes player HP, mana, active effects, boss HP, and potentially the turn number.
Spells have costs and effects (instant damage/heal, timed armor, timed damage over time, timed mana regeneration).
Part 2 adds a damage-over-time effect to the player at the start of each of their turns.
I can represent the game state as a tuple or a class.
The search will involve exploring possible spell casts at each player turn.
I need to keep track of the mana spent.
The search should stop when the boss HP reaches 0 or the player HP reaches 0.
I need to handle the timing of effects correctly.
I should use a way to avoid redundant states or infinite loops, possibly by keeping track of visited states or by bounding the search depth/mana spent.
Since I need the minimum mana spent, a breadth-first search might be more appropriate.
The state in the BFS should include the current mana spent.
The BFS should start with the initial state and explore reachable states by casting spells.
The transitions between states involve applying spell effects, boss attacks, and the new Part 2 rule.
I need to carefully simulate the order of operations on each turn: apply effects, cast spell (player turn), boss attack (boss turn).
For Part 2, the player loses 1 HP at the start of their turn.

Let's define the game state:

Player HP

Player Mana

Active effects (type, duration)

Boss HP

The actions are casting spells.

BFS Algorithm:

Initialize the starting state with mana spent 0.

Use a queue to store states to explore.

Use a set to store visited states to avoid loops.

While the queue is not empty:
a. Dequeue a state.
b. If it's the player's turn:
i. Apply start-of-turn effects.
ii. Apply Part 2 damage.
iii. If player HP <= 0, continue.
iv. If boss HP <= 0, return the mana spent.
v. Iterate through all possible spells.
vi. If the spell can be cast (enough mana, effect not active), create the new state after casting the spell.
vii. If the new state has not been visited, add it to the visited set and enqueue it.
c. If it's the boss's turn:
i. Apply start-of-turn effects.
ii. If player HP <= 0, continue.
iii. If boss HP <= 0, continue.
iv. Boss attacks.
v. Create the new state.
vi. If the new state has not been visited, add it to the visited set and enqueue it.

Need to represent effects: (type, timer).
Need a function to apply effects.
Need a function to simulate a turn.

The state should also include whose turn it is.

Optimization: Keep track of the minimum mana spent to reach a certain state to avoid exploring paths with higher mana cost.

The BFS should explore states with increasing mana spent. The first time we reach a winning state, that will be the minimum mana cost.

```python
import sys
from collections import deque

def solve():
    boss_hp_start = int(sys.stdin.readline().split(': ')[1])
    boss_damage = int(sys.stdin.readline().split(': ')[1])

    def apply_effects(player_hp, player_mana, boss_hp, effects):
        new_effects = {}
        player_armor = 0
        poison_damage = 0
        recharge_gain = 0

        for effect, timer in effects.items():
            if effect == 'Shield':
                player_armor = 7
            elif effect == 'Poison':
                poison_damage += 3
            elif effect == 'Recharge':
                recharge_gain += 101

            new_timer = timer - 1
            if new_timer > 0:
                new_effects[effect] = new_timer

        boss_hp -= poison_damage
        player_mana += recharge_gain
        return player_hp, player_mana, boss_hp, new_effects, player_armor

    def boss_turn(player_hp, player_mana, boss_hp, effects, boss_damage):
        player_hp_after_effects, player_mana_after_effects, boss_hp_after_effects, new_effects, player_armor = apply_effects(player_hp, player_mana, boss_hp, effects)
        if boss_hp_after_effects <= 0:
            return player_hp_after_effects, player_mana_after_effects, boss_hp_after_effects, new_effects, False

        damage = max(1, boss_damage - player_armor)
        player_hp_after_attack = player_hp_after_effects - damage
        return player_hp_after_attack, player_mana_after_effects, boss_hp_after_effects, new_effects, True

    def player_turn(player_hp, player_mana, boss_hp, effects, spell):
        player_hp -= 1
        if player_hp <= 0:
            return None

        player_hp_after_dmg, player_mana_after_dmg, boss_hp_after_dmg, new_effects, _ = apply_effects(player_hp, player_mana, boss_hp, effects)
        if boss_hp_after_dmg <= 0:
            return (player_hp_after_dmg, player_mana_after_dmg, boss_hp_after_dmg, new_effects)

        spell_cost = 0
        new_mana = player_mana_after_dmg
        new_boss_hp = boss_hp_after_dmg
        new_player_hp = player_hp_after_dmg
        new_effects_player = new_effects.copy()

        if spell == 'Magic Missile':
            spell_cost = 53
            new_boss_hp -= 4
        elif spell == 'Drain':
            spell_cost = 73
            new_boss_hp -= 2
            new_player_hp += 2
        elif spell == 'Shield':
            spell_cost = 113
            if 'Shield' not in new_effects_player:
                new_effects_player['Shield'] = 6
            else:
                return None
        elif spell == 'Poison':
            spell_cost = 173
            if 'Poison' not in new_effects_player:
                new_effects_player['Poison'] = 6
            else:
                return None
        elif spell == 'Recharge':
            spell_cost = 229
            if 'Recharge' not in new_effects_player:
                new_effects_player['Recharge'] = 5
            else:
                return None

        if new_mana >= spell_cost:
            return (new_player_hp, new_mana - spell_cost, new_boss_hp, new_effects_player)
        else:
            return None

    q = deque([(50, 500, boss_hp_start, {}, 0)])
    visited = set()
    min_mana = float('inf')

    while q:
        player_hp, player_mana, boss_hp, effects, mana_spent = q.popleft()

        if (player_hp, player_mana, boss_hp, tuple(sorted(effects.items()))) in visited:
            continue
        visited.add((player_hp, player_mana, boss_hp, tuple(sorted(effects.items()))))

        possible_spells = ['Magic Missile', 'Drain', 'Shield', 'Poison', 'Recharge']

        for spell in possible_spells:
            next_state = player_turn(player_hp, player_mana, boss_hp, effects, spell)
            if next_state:
                next_player_hp, next_player_mana, next_boss_hp, next_effects = next_state
                new_mana_spent = mana_spent + {'Magic Missile': 53, 'Drain': 73, 'Shield': 113, 'Poison': 173, 'Recharge': 229}[spell]

                if next_boss_hp <= 0:
                    min_mana = min(min_mana, new_mana_spent)
                    continue

                boss_attack_result = boss_turn(next_player_hp, next_player_mana, next_boss_hp, next_effects, boss_damage)
                if boss_attack_result:
                    boss_player_hp, boss_player_mana, boss_boss_hp, boss_effects, can_continue = boss_attack_result
                    if can_continue and boss_player_hp > 0:
                        if (boss_player_hp, boss_player_mana, boss_boss_hp, tuple(sorted(boss_effects.items()))) not in visited:
                            q.append((boss_player_hp, boss_player_mana, boss_boss_hp, boss_effects, new_mana_spent))

    print(min_mana)

if __name__ == "__main__":
    solve()
  ```
                               """))
