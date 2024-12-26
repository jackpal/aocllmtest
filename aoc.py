from aocd.models import Puzzle

def puzzle_prose(puzzle_year, puzzle_day, puzzle_part):
    return Puzzle(year=puzzle_year, day=puzzle_day)._get_prose()

def input(puzzle_year, puzzle_day):
    return Puzzle(year=puzzle_year, day=puzzle_day).input_data

def check_answer(puzzle_year, puzzle_day, puzzle_part, answer):
    puzzle = Puzzle(year=puzzle_year, day=puzzle_day)
    if puzzle_part == 1:
        if puzzle.answered_a:
            return puzzle.answer_a == answer
        puzzle.answer_a = answer
        return puzzle.answered_a
    elif puzzle_part == 2:
        if puzzle.answered_b:
            return puzzle.answer_b == answer
        puzzle.answer_b = answer
        return puzzle.answered_b
    else:
        raise Exception(f'Unknown part {puzzle_part}')