# strategy.py
import db
import aoc_api
import time
from typing import List, Tuple, Dict

def get_next_experiment() -> Tuple:
    """Determines the next experiment to run based on the defined strategy.

    Returns:
        A tuple representing the next experiment (model_family, model_name, year, day, part, timeout, previous_attempt_timed_out), 
        or None if there are no more experiments to run.
    """

    # Check for incomplete experiments first
    incomplete_experiments = db.get_incomplete_experiments()
    if incomplete_experiments:
        # Prioritize based on strategy (e.g., shortest timeout first)
        incomplete_experiments.sort(key=lambda x: x[10] if x[10] is not None else 0) 
        experiment = incomplete_experiments[0]
        return (experiment[1], experiment[2], experiment[3], experiment[4], experiment[5], experiment[10], experiment[13])
    
    quota_exceeded_families = db.get_quota_exceeded_families()

    # 1. Get available model families and models
    available_model_families = [fam for fam in aoc_api.model_families() if fam not in quota_exceeded_families]

    if not available_model_families:
        print("All model families have exceeded their quota. Waiting...")
        return None
    
    
    # 2. Define the order of years, days, and parts (strategy)
    years = range(2024, 2014, -1)  # Most recent year first
    days = range(1, 26)  # Lower numbered days first
    parts = range(1, 3)
    
    # Iterate through the combinations based on the strategy
    for model_family in available_model_families:
        for model_name in aoc_api.models(model_family):
            for year in years:
                for day in days:
                    for part in parts:
                        # Check if this experiment already exists in the database
                        # Note: This assumes that the combination of model_family, model_name, year, day, and part uniquely identifies an experiment.
                        # You might need a more robust way to check for existing experiments if this assumption is not valid.
                        
                        
                        conn = db.sqlite3.connect(db.DATABASE_NAME)
                        cursor = conn.cursor()
                        cursor.execute("""
                            SELECT * FROM experiments
                            WHERE model_family = ? AND model_name = ? AND puzzle_year = ? AND puzzle_day = ? AND puzzle_part = ?
                        """, (model_family, model_name, year, day, part))
                        existing_experiment = cursor.fetchone()
                        conn.close()
                        
                        
                        if not existing_experiment:
                            return (model_family, model_name, year, day, part, 10, False)  # Default timeout 10 seconds

    return None  # No new experiments to run

def run_experiment(model_family: str, model_name: str, year: int, day: int, part: int, timeout:int, previous_attempt_timed_out: bool) -> None:
    """Runs a single experiment.

    Args:
        model_family: The model family.
        model_name: The model name.
        year: The puzzle year.
        day: The puzzle day.
        part: The puzzle part.
        timeout: the timeout in seconds
        previous_attempt_timed_out: Whether or not a previous attempt timed out
    """
    print(f"Running experiment: {model_family} {model_name}, Year: {year}, Day: {day}, Part: {part}, Timeout: {timeout}, Previous Timeout: {previous_attempt_timed_out}")

    # 1. Create prompt
    prompt_result = aoc_api.create_prompt(model_family, model_name, year, day, part, previous_attempt_timed_out)
    
    if prompt_result[0] == 'error':
        print(f"Error creating prompt: {prompt_result[1]}")
        db.add_experiment(model_family, model_name, year, day, part, None, previous_attempt_timed_out)
        experiment_id = db.sqlite3.connect(db.DATABASE_NAME).cursor().lastrowid
        db.update_experiment(experiment_id, None, 'error', None, None, None, prompt_result[1])
        return
    elif prompt_result[0] == 'sequence':
        print(f"Sequence error: Need to solve {prompt_result[1]} first.")
        
        # Recursively solve the prerequisite puzzle
        prereq_year, prereq_day, prereq_part = prompt_result[1]
        run_experiment(model_family, model_name, prereq_year, prereq_day, prereq_part, 10, False)
        # After solving the prerequisite, try the current experiment again.
        run_experiment(model_family, model_name, year, day, part, timeout, previous_attempt_timed_out)
        return
    else:
        full_prompt = prompt_result[1]

    # 2. Add experiment to database
    experiment_id = db.add_experiment(model_family, model_name, year, day, part, full_prompt, previous_attempt_timed_out)
        

    # 3. Generate program
    program_result = aoc_api.generate_program(model_family, model_name, full_prompt, year, day, part)

    if program_result[0] == 'error':
        print(f"Error generating program: {program_result[1]}")
        db.update_experiment(experiment_id, None, 'error', None, None, None, program_result[1])
        return
    elif program_result[0] == 'quota':
        print(f"Quota exceeded for {model_family}: {program_result[1]}")
        db.record_quota_exceeded(model_family)
        db.update_experiment(experiment_id, None, 'quota', None, None, None, program_result[1])

        return
    else:
        generated_program = program_result[1]

    # 4. Run program
    run_result = aoc_api.run_program(generated_program, timeout)

    if run_result[0] == 'error':
        print(f"Error running program: {run_result[1]}")
        db.update_experiment(experiment_id, generated_program, 'error', None, None, timeout, run_result[1])
        return
    elif run_result[0] == 'timeout':
        print(f"Program timed out after {timeout} seconds.")
        
        if previous_attempt_timed_out == False:
          # Regenerate the prompt, marking it as having timed out previously
          db.update_experiment(experiment_id, generated_program, 'timeout', None, None, timeout, f"Program timed out after {timeout} seconds.")
          run_experiment(model_family, model_name, year, day, part, timeout, True)
          return
        elif timeout == 10:
          
          # Try again with a longer timeout
          db.update_experiment(experiment_id, generated_program, 'timeout', None, None, timeout, f"Program timed out after {timeout} seconds.")
          run_experiment(model_family, model_name, year, day, part, 100, True)
          return
        elif timeout == 100:
          # Try again with an even longer timeout
          db.update_experiment(experiment_id, generated_program, 'timeout', None, None, timeout, f"Program timed out after {timeout} seconds.")
          run_experiment(model_family, model_name, year, day, part, 1000, True)
          return
        else:
          db.update_experiment(experiment_id, generated_program, 'timeout', None, None, timeout, f"Program timed out after {timeout} seconds.")
          return

          
    else:
        program_output = run_result[1]

    # 5. Check answer
    is_correct = aoc_api.check_answer(year, day, part, program_output)

    # 6. Update experiment in database
    db.update_experiment(experiment_id, generated_program, 'success', program_output, is_correct, timeout, None)

    print(f"Experiment {experiment_id} completed. Correct: {is_correct}")

def run_all_experiments() -> None:
    """Runs experiments until there are no more to run or until interrupted."""
    db.create_tables()

    while True:
        next_experiment = get_next_experiment()
        if next_experiment is None:
            print("No more experiments to run at the moment.")
            time.sleep(60) # Wait for a minute before checking again, in case quota limits reset
            
        else:
            run_experiment(*next_experiment)