import aoc
import gemini
import perform
import prompt
from typing import List, Tuple, Union

def model_families() -> List[str]:
    """
    Returns a list of the available model families.

    Returns:
        List[str]: A list of model family names.
    """
    return ["Gemini"]  

def models(model_family: str) -> List[str]:
    """
    Returns a list of models for a given model family.

    Args:
        model_family (str): The name of the model family.

    Returns:
        List[str]: A list of model names within the specified family.
    """
    if model_family == "Gemini":
        return ['gemini-exp-1206', 'gemini-2.0-flash-exp', 'gemini-2.0-flash-thinking-exp-1219']
    else:
        return []

def create_prompt(model_family: str, model_name: str, puzzle_year: int, puzzle_day: int, puzzle_part: int, previous_attempt_timed_out: bool) -> Tuple[str, Union[str, Tuple[int, int, int]]]:
    """Creates a prompt suitable for solving the given puzzle.

    Args:
        model_family (str): The name of the model family.
        model_name (str): The name of the model.
        puzzle_year (int): The year of the puzzle.
        puzzle_day (int): The day of the puzzle.
        puzzle_part (int): The part of the puzzle (1 or 2).
        previous_attempt_timed_out (bool): True if a previous attempt to solve this puzzle timed out, False otherwise.

    Returns:
        Tuple[str, Union[str, Tuple[int, int, int]]]: A tuple indicating the result of the prompt creation:
            - ('error', <error message>)
            - ('sequence', (year, day, part))
            - ('success', <prompt>)
    """
    # Simulate some logic for sequence checking and prompt generation
    if puzzle_year == 2023 and puzzle_day == 1 and puzzle_part == 2:
         return ("sequence", (2023, 1, 1))
    elif puzzle_year == 2024 and puzzle_day == 5 and puzzle_part == 2:
         return ("sequence", (2024, 5, 1))

    
    prompt = f"Solve Advent of Code {puzzle_year}, Day {puzzle_day}, Part {puzzle_part} using {model_family} {model_name}."
    if previous_attempt_timed_out:
        prompt += " Note: Previous attempts timed out."
    return ("success", prompt)

def generate_program(model_family: str, model_name: str, full_prompt: str, puzzle_year: int, puzzle_day: int, puzzle_part: int) -> Tuple[str, str]:
    """Generates a program using the given arguments.

    Args:
        model_family (str): The name of the model family.
        model_name (str): The name of the model.
        full_prompt (str): The full prompt for the model.
        puzzle_year (int): The year of the puzzle.
        puzzle_day (int): The day of the puzzle.
        puzzle_part (int): The part of the puzzle (1 or 2).

    Returns:
        Tuple[str, str]: A tuple indicating the result of the program generation:
            - ('error', <error message>)
            - ('quota', <quota message>)
            - ('success', <generated program>)
    """
    # Simulate some logic for program generation and quota errors
    if model_family == "FamilyB" and puzzle_year == 2023 and puzzle_day == 2:
        return ("quota", "Quota exceeded for FamilyB. Try again later.")
    
    if model_family == "FamilyA" and puzzle_year < 2018:
        return ("error", f"{model_family} does not support years before 2018")

    program = f"""
# Generated program for {puzzle_year}, Day {puzzle_day}, Part {puzzle_part}
# using {model_family} {model_name}

def solve():
    # Simulated solution
    return "{puzzle_year}-{puzzle_day}-{puzzle_part} solved by {model_name}"

if __name__ == "__main__":
    print(solve())
"""
    return ("success", program)

def run_program(program: str, timeout: int) -> Tuple[str, Union[str, int]]:
    """Tests the program in a safe environment.

    Args:
        program (str): The program code to run.
        timeout (int): The timeout in seconds.

    Returns:
        Tuple[str, Union[str, int]]: A tuple indicating the result of running the program:
            - ('error', <error message>)
            - ('timeout', <int timeout value>)
            - ('success', <output of program>)
    """
    assert(program)
    assert(timeout > 0)
    input = aoc.input(puzzle_year, puzzle_day)
    # Simulate running the program and potential timeouts
    asse
    
    if "timeout" in program:
      if timeout < 1000:
        return ("timeout", timeout)
      else:
        return ("error", "Program still timed out after multiple attempts with increasing timeouts.")
        
    
    
    if "error" in program:
      return ("error", "Program failed with an error.")
    else:
      # Simulate successful execution and extract the result
      lines = program.split('\n')
      for line in lines:
        if "return" in line:
            return ("success", line.split('"')[1])
      return ("success", "Program ran successfully, but did not produce the expected output format")

def check_answer(puzzle_year: int, puzzle_day: int, puzzle_part: int, answer: str) -> bool:
    """Checks if the given answer is correct for the given puzzle.

    Args:
        puzzle_year (int): The year of the puzzle.
        puzzle_day (int): The day of the puzzle.
        puzzle_part (int): The part of the puzzle (1 or 2).
        answer (str): The answer to check.

    Returns:
        bool: True if the answer is correct, False otherwise.
    """
    return aoc.check_answer(puzzle_year, puzzle_day, puzzle_part, answer)