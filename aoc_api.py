import aoc
import gemini
import perform
import prompt
from typing import List, Tuple

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

def create_prompt(model_family: str, model_name: str, puzzle_year: int, puzzle_day: int, puzzle_part: int, puzzle_prose: str, previous_attempt_timed_out: bool) -> Tuple[str, str]:
    """
    Creates a prompt suitable for solving the given puzzle.

    Args:
        model_family (str): The model family.
        model_name (str): The model name.
        puzzle_year (int): The year of the puzzle.
        puzzle_day (int): The day of the puzzle.
        puzzle_part (int): The part of the puzzle (1 or 2).
        puzzle_prose (str): The text description of the puzzle.
        previous_attempt_timed_out (bool): True if a previous attempt to solve this puzzle timed out, False otherwise.

    Returns:
        Tuple[str, str]: A tuple where the first element is a status string 
                        ('error', 'sequence', or 'success') and the second element 
                        is either an error message, a sequence message, or the generated prompt.
    """
    # Replace this with your actual prompt generation logic
    if puzzle_prose is None:
        return "error", "Puzzle prose is missing."

    if previous_attempt_timed_out:
        prompt = f"Solve Advent of Code {puzzle_year}, Day {puzzle_day}, Part {puzzle_part}. Previous attempt timed out. Puzzle Description: {puzzle_prose}"
    else:
        prompt = f"Solve Advent of Code {puzzle_year}, Day {puzzle_day}, Part {puzzle_part}. Puzzle Description: {puzzle_prose}"

    return "success", prompt

def generate_program(model_family: str, model_name: str, full_prompt: str, puzzle_year: int, puzzle_day: int, puzzle_part: int) -> Tuple[str, str]:
    """
    Generates a program using the given arguments.

    Args:
        model_family (str): The model family.
        model_name (str): The model name.
        full_prompt (str): The complete prompt for the model.
        puzzle_year (int): The year of the puzzle.
        puzzle_day (int): The day of the puzzle.
        puzzle_part (int): The part of the puzzle (1 or 2).

    Returns:
        Tuple[str, str]: A tuple where the first element is a status string 
                        ('error', 'quota', or 'success') and the second element 
                        is either an error message, a quota message, or the generated program.
    """
    # Replace this with your actual program generation logic (e.g., API call to a model)
    if model_family == "family_that_hits_quota":
        return "quota", "Quota limit reached for this model family."
    
    if model_family == "family_with_errors":
        return "error", "An error occurred during program generation."

    # Simulate generating a program
    program = f"""
# Generated program for Advent of Code {puzzle_year}, Day {puzzle_day}, Part {puzzle_part}
def solve():
    # Placeholder for puzzle-solving logic
    print("This is a placeholder program.")
    print("Model: {model_family} {model_name}")
    print("Year: {puzzle_year}, Day: {puzzle_day}, Part: {puzzle_part}")
    return "42" 

solve()
"""
    return "success", program

def run_program(program: str, timeout: int) -> Tuple[str, str | int]:
    """
    Tests the program in a safe environment.

    Args:
        program (str): The program to run.
        timeout (int): The time in seconds that the program is allowed to run before timing out.

    Returns:
        Tuple[str, str | int]: A tuple where the first element is a status string 
                             ('error', 'timeout', or 'success') and the second 
                             element is either an error message, the timeout value, or the output of the program.
    """
    # Replace this with your actual program execution logic (e.g., using a sandbox)
    
    # Simulate running the program with potential timeout or error
    if "timeout" in program:
        return "timeout", timeout
    elif "error" in program:
        return "error", "Runtime error in program."
    else:
        return "success", "42"

def check_answer(puzzle_year: int, puzzle_day: int, puzzle_part: int, answer: str) -> bool:
    """
    Checks if the given answer is correct for the given puzzle.

    Args:
        puzzle_year (int): The year of the puzzle.
        puzzle_day (int): The day of the puzzle.
        puzzle_part (int): The part of the puzzle (1 or 2).
        answer (str): The answer to check.

    Returns:
        bool: True if the answer is correct, False otherwise.
    """
    # Replace this with your actual answer checking logic (e.g., against a known solution)
    # For demonstration, let's assume the answer "42" is always correct
    return answer == "42"