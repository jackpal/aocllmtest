# Prompts used to generate the aocllm test app

```
Initial prompt

You are an expert SQLite and Python 3 programmer.

You are writing a Python app that will run a series of tests to see how well different models and different prompts work on writing code to solve the Advent of Code puzzles. The app will keep track of the test results in a SQL database. The app will provide a Flask web based API for viewing the progress of the tests and the results of the test. The app will also provide command-line arguments for generating csv output giving the results of the tests.

Advent of Code is a collection of puzzles that are designed to be solved with computer assistance. The contest runs yearly, for 25 days each year. Currently there are 10 years, from 2015 to 2024. Each year has 25 days of puzzles, and each day’s puzzle has 2 parts. Day 25, part 2, is special because it is automatically solved when all the other puzzles of that year have been solved.

For a given year and day, part 1 of the puzzle has to be solved first, before the instructions for part 2 become available. Therefore part 1 of a given year and day must be solved before part 2 is solved.

The following functions already exist, in a library named aoc_api, and you should call them as needed to help with the problem:

model_families() -> List[str]

Returns a list of the available model families

models(model_family: str) -> List[str]

Returns a list of models for a given model family.

create_prompt(model_family: str, model_name: str, puzzle_year: int, puzzle_day: int, puzzle_part: int, previous_attempt_timed_out: boolean) -> Tuple[str, str|Tuple[int,int,int]]

This function creates a prompt suitable for solving the given puzzle.

The previous_attempt_timed_out argument is initially False, but is set to true if a previous attempt to solve this particular model-family/model-name/year/day/part timed out.

This function returns the prompt as a tuple:

(‘error’, <error message>)
(‘sequence’, (year, day, part))
(‘success’, <prompt>)

A ‘sequence’ message means the puzzle can’t be attempted yet, because another puzzle needs to be solved first.The (year, day, part) of the other puzzle is returned as the second item in the tuple.  In general, for a given puzzle year and puzzle day, part 1 has to be solved first before part 2 can be attempted.
 
generate_program(model_family: str, model_name: str, full_prompt: str, puzzle_year: int, puzzle_day: int, puzzle_part: int)  -> tuple[str, str]

This function generates a program using the given arguments. It returns a tuple where the first item is an enumerated string ‘error’ or ‘success’. The second item depends on the first item:

(‘error’, <error message>)
(‘quota’, <quota message>)
(‘success’, <generated program>)

A quota is a special kind of error message. It means that the generate_program process failed for this particular model_family, but might succeed if it was tried again after a period of time elapsed.

run_program(program: str, timeout: int) -> tuple[str, str|int]

This function tests the program in a safe environment. The timeout is the time in seconds that the program is allowed to run before timing out. It returns a tuple where the first item is an enumerated string ‘error’ or ‘success’. The second item depends on the first item:

(‘error’, <error message>)
(‘timeout’, <int timeout value>) 
(‘success’, <output of program>)


check_answer(puzzle_year: int, puzzle_day: int, puzzle_part: int, answer:  str) -> bool

This function checks if the given answer is correct for the given puzzle, and returns True if it is correct, or False if it is not correct.

OK, your job is:

Write a python program to test how well the different models from the different model families can solve Advent of Code puzzles.

It takes a long time to run all the tests, and the program may be killed and restarted during the testing process. Use a SQL database to keep track of the progress.

Provide a way of querying the database to tell the current status of the testing run, and for summarizing the results of the experiments.

Some interesting queries are:


How many experiments have been run so far, and how many more experiments are there?

Rank the model families by how well they solve the tests.

Within each model family, rank the models by how well they solve the tests.

How difficult are the different puzzle years? Rank them by how hard they are to solve.

Some strategies for deciding what order to test things in:

Test the most recent year first, because that year is likely to not yet be in the training set for the models, so it is likely to give a more accurate representation.

Test the lower-numbered days of each year first, because they are likely to be easier problems and so likely to be successful.

Test all the members of a model_family on the same problem, because it’s interesting to see if there are any differences.

Initially use a short timeout value (say 10 seconds). For problems that timeout with the short value, try regenerating the prompt with previous_attempt_timed_out:True. If that still times out, try using longer timeout values (100 seconds, and finally 1000 seconds.)

If a given call to generate_program fails with a ‘quota’ error, remember that fact, and don’t try to generate_program for the same model_family for 1 hour. You can generate for other model families if there are any other model families that are not also waiting for their 1 hour timeout to expire.

Now generate the following files to implement the program. This is a big program, so generate it in parts:

An aoc_api.py file that contains stub implementations of the aoc_api functions. Use Python typing hints and generate doc strings.

A db.py file that contains all the database functions

A strategy.py file that contains the strategy functions for deciding which tests to run in which order, and runs the tests.

A webserver.py file that contains the web server functions

A main.py file that contains the command line argument parsing and calls all the other functions.


Generate the stub aoc_api.py file now:

—

Generate the db.py file now

—

Generate the strategy.py file now

—

Generate the webserver.py file now

---

Generate the main.py file now

—

Generate a VS code launch.json file with configurations for generating the report, running the experiments without the web server, and running the experiments with the web server.

Running the experiments with the web server should be the default configuration.

I want to be able to run under the vs code python debugger or without the debugger.


```