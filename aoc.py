from aocd.models import Puzzle
from bs4 import BeautifulSoup

def puzzle_solved(puzzle_year, puzzle_day, puzzle_part):
    puzzle = Puzzle(year=puzzle_year, day=puzzle_day)
    if puzzle_part == 1:
        return puzzle.answered_a
    elif puzzle_part == 2:
        return puzzle.answered_b
    else:
        raise Exception(f'Unknown part {puzzle_part}')

def puzzle_prose(puzzle_year, puzzle_day, puzzle_part):
    prose = BeautifulSoup(Puzzle(year=puzzle_year, day=puzzle_day)._get_prose(), features="html.parser")
    articles = [article.text for article in prose.find_all('article', class_='day-desc')]
    if not articles:
        return prose.text
    if puzzle_part == 1:
        return articles[0]
    return '\n'.join(articles)

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
        if not puzzle.answered_a:
            raise Exception(f'Can\'t check part 2 before answering part 1.')
        # Manually check this because the Puzzle class will raise an exception
        # if answer_b is the same as answer_a.
        if puzzle.answer_a == answer:
            return False
        puzzle.answer_b = answer
        return puzzle.answered_b
    else:
        raise Exception(f'Unknown part {puzzle_part}')
