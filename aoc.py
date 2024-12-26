from aocd.models import Puzzle
from bs4 import BeautifulSoup
import db

def _puzzle_and_part_from_puzzle_id(conn, puzzle_id):
    assert(puzzle_id)
    puzzle_dict = db.get_puzzle_row(conn, puzzle_id)
    assert(puzzle_dict)
    year, day, part = puzzle_dict['year'], puzzle_dict['day'], puzzle_dict['part']
    return Puzzle(year=year, day=day), part

def _puzzle_prose(puzzle, id):
    """id 0 means the prose before either part is answered.
    id 1 is the prose after the first part is answered
    id 2 is the prose after both parts are answered
    """
    return puzzle._get_prose()
    
    # def puzzle_prose_path(puzzle, id):
    #     if id == 0:
    #         return puzzle.prose0_path
    #     if id == 1:
    #         return puzzle.prose1_path
    #     if id == 2:
    #         return puzzle.prose2_path
    
    # with open(puzzle_prose_path(puzzle, id), 'r') as file:
    #     text = file.read()
    
    # soup = BeautifulSoup(text.split("<main>")[-1])
    # return soup.text

def puzzle_prose(conn, puzzle_id):
    assert(puzzle_id)
    puzzle, part = _puzzle_and_part_from_puzzle_id(conn, puzzle_id)
    return _puzzle_prose(puzzle, part-1)

def input(conn, puzzle_id):
    assert(puzzle_id)
    puzzle, part = _puzzle_and_part_from_puzzle_id(conn, puzzle_id)
    return puzzle.input_data

def check_answer(conn, puzzle_id, answer):
    puzzle, part = _puzzle_and_part_from_puzzle_id(conn, puzzle_id)
    if part == 1:
        if puzzle.answered_a:
            return puzzle.answer_a == answer
        puzzle.answer_a = answer
        return puzzle.answered_a
    elif part == 2:
        if puzzle.answered_b:
            return puzzle.answer_b == answer
        puzzle.answer_b = answer
        return puzzle.answered_b
    else:
        raise Exception(f'Unknown part {part}')