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

def puzzle_instructions(puzzle_year: int, puzzle_day: int, puzzle_part: int) -> Tuple[str, str | Tuple[int, int, int]]:
    """Returns the puzzle instructions."""
    if puzzle_part > 1:
        precursor_puzzle_part = puzzle_part-1
        if not aoc.puzzle_solved(puzzle_year, puzzle_day, precursor_puzzle_part):
            return ('sequence', (puzzle_year, puzzle_day, precursor_puzzle_part))

    puzzle_prose = aoc.puzzle_prose(puzzle_year, puzzle_day, puzzle_part)
    
    return ('success', puzzle_prose)

def create_prompt(model_family: str, model_name: str, puzzle_year: int, puzzle_day: int, puzzle_part: int, previous_attempt_timed_out: bool, puzzle_instructions: str) -> Tuple[str, Union[str, Tuple[int, int, int]]]:
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
            - ('success', <prompt>)
    """
        
    system_prompt = prompt.system_prompt()
    
    full_prompt = system_prompt + '\n\n' + puzzle_instructions + '\n\nOnly print the answer for part {puzzle_part}\n'

    if previous_attempt_timed_out:
        full_prompt += " Note: Previous attempts to solve this puzzle timed out. Use algorithms with good O(n) performance, and techniques such as @cache to make the program run faster. The input may be very large."
    return ("success", full_prompt)

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
    assert(model_family == 'Gemini')
    try:
        result, text = gemini.generate(model_name, full_prompt)
        if result == 'success':
            return ('success', text)
        else:
            return ('error', 'No program found. Text: {text}')
    except Exception as e:
        exception_str = str(e)
        if "429" in exception_str:
            # Assume it's a quota issue.
            return ('quota', exception_str)
        return ('error', exception_str)

def run_program(puzzle_year: int, puzzle_day: int, puzzle_part: int, program: str, timeout: int) -> Tuple[str, Union[str, int]]:
    """Tests the program in a safe environment.

    Args:
        puzzle_year (int): The year of the puzzle.
        puzzle_day (int): The day of the puzzle.
        puzzle_part (int): The part of the puzzle (1 or 2).
        program (str): The program code to run.
        timeout (int): The timeout in seconds.

    Returns:
        Tuple[str, Union[str, int]]: A tuple indicating the result of running the program:
            - ('error', <error message>)
            - ('timeout', <int timeout value>)
            - ('answer', <answer>)
    """
    assert(program)
    if timeout == None:
        timeout = 10
    assert(timeout > 0)
    input = aoc.input(puzzle_year, puzzle_day)
    result, answer = perform.run(program, puzzle_part, input, timeout)
    if result == 'error':
        print(f'computation failed: {answer}')
        return (result, answer)
    elif result == 'timeout':
        print('computation timed out')
        return (result, timeout)
    elif result == 'success':
        print(f'computation finished, answer: \'{answer}\'')
        return('answer', answer)
    else:
        raise Exception(f'Unknown result {result}')

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
