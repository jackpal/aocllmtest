# Prompts used to generate the aocllm test app

Jack Palevich
Dec 26, 2024

Initial prompt

You are an expert Python and SQLite programmer.

Summary of task:

You are writing a set of four Python apps that will run a series of experiments to see how well different LLM models and different prompts work on writing code to solve the Advent of Code puzzles. 

The apps will keep track of the experiment results and the current state of the overall process  in a SQLite database. One app will conduct the experiments. A second app will provide a web UI for viewing the status of the experiments. A third app will allow editing the experiment database using command line flags, and a fourth app will allow generating reports using command line flags.

Advent of Code is a collection of puzzles that are designed to be solved with computer assistance. The contest runs yearly, for 25 days each year. Currently there are 10 years, from 2015 to 2024. Each year has 25 days of puzzles, and each day’s puzzle has 2 parts. Day 25, part 2, is special because it is automatically solved when all the other puzzles of that year have been solved.

For a given year and day, part 1 of the puzzle has to be solved first, before the instructions for part 2 become available. Therefore part 1 of a given year and day must be solved before part 2 is solved.

To help you, there is a library in the file aoc_api.py that has the following predefined functions. Generate stub versions of these functions.

modelfamilies() -> List[str]

Returns a list of the available model families

models(model_family: str) -> List[str]

Returns a list of models for a given model family.

puzzle_instructions(puzzle_year: int, puzzle_day: int, puzzle_part: int) ->  Tuple[str, strstr|Tuple[int,int,int]]

Returns the puzzle instructions, which are required for creating a prompt. The prose for part 2 puzzles is not available until after part 1 of the puzzle has been solved.

Returns the puzzle description as a tuple:

(‘error’, <error message>)
(‘sequence’, (year, day, part))
(‘success’, <instructions>)

‘error’ means that an error has occurred.
‘sequence’ means the function will not succeed until after the given (year, day, part) puzzle has been solved.
‘success’ means the function succeeded, and the puzzle instructions are the second item in the tuple.

create_prompt(model_family: str, model_name: str, puzzle_year: int, puzzle_day: int, puzzle_part: int, previous_attempt_timed_out: boolean, puzzle_instructions: str) -> Tuple[str, str|Tuple[int,int,int]]

This function creates a prompt suitable for solving the given puzzle.

The previous_attempt_timed_out argument is initially False, but is set to true if a previous attempt to solve this particular model-family/model-name/year/day/part timed out.

This function returns the prompt as a tuple:

(‘error’, <error message>)
(‘success’, <prompt>)
 
generate_program(model_family: str, model_name: str, full_prompt: str, puzzle_year: int, puzzle_day: int, puzzle_part: int)  -> tuple[str, str]

This function generates a program using the given arguments. It returns a tuple where the first item is an enumerated string ‘error’ or ‘success’. The second item depends on the first item:

(‘error’, <error message>)
(‘quota’, <quota message>)
(‘success’, <generated program>)

A quota is a special kind of error message. It means that the generate_program process failed for this particular model_family, but might succeed if it was tried again after a period of time elapsed.

run_program(puzzle_year: int, puzzle_day: int, puzzle_part: int, program: str, timeout: int) -> tuple[str, str|int]

This function tests the program in a safe environment. The timeout is the time in seconds that the program is allowed to run before timing out. It returns a tuple where the first item is an enumerated string ‘error’ ‘timeout’, or ‘answer’. The second item depends on the first item:

(‘error’, <error message>)
(‘timeout’, <int timeout value>) 
(‘answer’, <answer>)

The answer may be correct, or it may be incorrect. You have to call check_answer (below) to check if it is correct.


check_answer(puzzle_year: int, puzzle_day: int, puzzle_part: int, answer:  str) -> bool

This function checks if the given answer is correct for the given puzzle, and returns True if it is correct, or False if it is not correct.

OK, your job is:

Design a sqlite database schema for storing the overall progress of the process and the experiment results.

Write four Python programs that communicate through a shared sqlite database:

1. An experiment runner that incrementally runs experiments to build up the experiment database that says how well the different models from the different model families can solve Advent of Code puzzles.

It takes a long time to run all the tests, and the program may be killed and restarted during the testing process. Use a SQLite database to keep track of the progress.


2. A web server that provides a nice UI for viewing the experiment database. Use the Flask web server library. Allow the web server port to be optionally specified from the command line.

3. A database manager app that can display the current database status and has command line arguments for deleting experiment records that match certain facts such as experiment id, mode_family, year, and so on.

3. A report generator that can display markdown and csv reports, and has command lines for controlling which reports are generated.

Provide a way of querying the database to tell the current status of the testing run, and for summarizing the results of the experiments.


Hints for the database

Puzzles are uniquely identified by the tuple year,day,part.

Puzzle experiment records are uniquely identified by model_family, model, tuple year, day, part. Only keep a record of one experiment for each tuple of model_family, model, tuple year, day, part. If a experiment fails due to an error or a timeout, or a quota exhaustion, you can try again. Once an experiment has generated an answer, even if the answer is wrong, do not try that experiment again.

Use unique constraints to prevent duplicate experiment entries.

Hints for the experiment runner

Test the puzzles in order of descending year. Within a year, test in order of increasing day. For a given year and day, test part 1 first before testing part 2.

For a given puzzle,  test all the models from all the model_families before moving on to the next puzzle.

Initially use a short timeout value (say 10 seconds). For problems that timeout with the short value, try regenerating the prompt with previous_attempt_timed_out:True. If that still times out, try using longer timeout values (100 seconds, and finally 1000 seconds.)

If a given call to generate_program fails with a ‘quota’ error, remember that fact, and don’t try to generate_program for the same model_family for 1 hour. You can generate for other model families if there are any other model families that are not also waiting for their 1 hour timeout to expire.

If there is nothing to do (due to not have any more puzzles to solve, or to all model family quotas being exhausted), the test engine should sleep until it is likely that there is something to do.

Hints for the report generator

The program will generate command-line and web-based reports. Some  interesting reports are:

What is the test engine currently doing. (Which puzzle is being tested, or is it waiting for a model family quota timeout, and if so, how much time until the timeout is over.)


How many experiments have been run so far, and how many more experiments are there?

Rank the model families by how well they solve the tests.

Within each model family, rank the models by how well they solve the tests.

How difficult are the different puzzle years? Rank them by how hard they are to solve.

Hints for the web server

The user would like to see the current status of the experiment runner, and also graphs, charts, and tables of interesting statistics. And the user would like to be able to delete experiment results by experiment id, model, and/or year.

In addition to the python code

Generate a VS code launch.json file with configurations for running each of the three programs.

Also provide a compound launch configuration that launches the experiment runner and the web server.

Launching the compound launch configuration should be the default configuration.

