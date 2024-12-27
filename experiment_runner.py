import sqlite3
import time
import aoc_api
import datetime

DATABASE = 'puzzles.db'
INITIAL_TIMEOUT = 10
TIMEOUT_VALUES = [10, 100, 1000]

def get_next_puzzle_to_solve(conn):
    """Gets the next puzzle that needs to be solved, in the correct order."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT year, day, part
        FROM puzzles
        WHERE solved = FALSE
        ORDER BY year DESC, day ASC, part ASC
        LIMIT 1
    """)
    result = cursor.fetchone()
    return result

def get_models_to_test(conn):
    """Gets all model families and models."""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM model_families")
    model_families = [row[0] for row in cursor.fetchall()]
    models_data = {}
    for family in model_families:
        cursor.execute("SELECT name FROM models WHERE family = ?", (family,))
        models_data[family] = [row[0] for row in cursor.fetchall()]
    return models_data

def is_quota_active(conn, model_family):
    """Checks if there's an active quota timeout for the model family."""
    cursor = conn.cursor()
    cursor.execute("SELECT timeout FROM quota_timeouts WHERE model_family = ?", (model_family,))
    result = cursor.fetchone()
    if result:
        timeout = datetime.datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S')
        if datetime.datetime.now() < timeout:
            return True
    return False

def add_quota_timeout(conn, model_family):
    """Adds or updates a quota timeout for the model family."""
    cursor = conn.cursor()
    timeout = datetime.datetime.now() + datetime.timedelta(hours=1)
    cursor.execute("""
        INSERT OR REPLACE INTO quota_timeouts (model_family, timeout)
        VALUES (?, ?)
    """, (model_family, timeout.strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()

def update_experiment(conn, experiment_id, status, result, answer, correct, timed_out, timeout):
    """Updates an experiment with the results."""
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE experiments
        SET status = ?, result = ?, answer = ?, correct = ?, timed_out = ?, timeout = ?, timestamp = ?
        WHERE id = ?
    """, (status, result, answer, correct, timed_out, timeout, datetime.datetime.now(), experiment_id))
    conn.commit()
    
def mark_puzzle_solved(conn, year, day, part):
    """Marks a puzzle as solved."""
    cursor = conn.cursor()
    cursor.execute("UPDATE puzzles SET solved = TRUE WHERE year = ? AND day = ? AND part = ?", (year, day, part))
    conn.commit()

def run_experiment(conn, model_family, model_name, year, day, part):
    """Runs an experiment for a given model, puzzle, and timeout."""
    cursor = conn.cursor()

    # Check if experiment already exists
    cursor.execute("""
        SELECT id, status, timed_out, timeout
        FROM experiments
        WHERE model_family = ? AND model_name = ? AND year = ? AND day = ? AND part = ?
    """, (model_family, model_name, year, day, part))
    existing_experiment = cursor.fetchone()

    if existing_experiment:
        experiment_id, status, timed_out, timeout = existing_experiment
        if status == 'answer':
            print(f"Skipping existing experiment for {model_family}/{model_name} on {year}/{day}/{part} (already has an answer)")
            return  # Already has an answer, don't re-run
        
        if timed_out:
            if timeout == TIMEOUT_VALUES[-1]:
                print(f"Skipping existing experiment for {model_family}/{model_name} on {year}/{day}/{part} (already timed out at max timeout)")
                return
            else:
                current_timeout_index = TIMEOUT_VALUES.index(timeout)
                timeout = TIMEOUT_VALUES[current_timeout_index + 1]
        else:
            timeout = INITIAL_TIMEOUT

    else:
        experiment_id = None
        timeout = INITIAL_TIMEOUT
        timed_out = False
    
    # Get puzzle instructions
    instructions_result = aoc_api.puzzle_instructions(year, day, part)
    if instructions_result[0] == 'error':
        print(f"Error getting instructions for {year}/{day}/{part}: {instructions_result[1]}")
        return
    elif instructions_result[0] == 'sequence':
        print(f"Need to solve {instructions_result[1]} before {year}/{day}/{part}")
        return
    else:
        puzzle_instructions = instructions_result[1]

    # Create prompt
    prompt_result = aoc_api.create_prompt(model_family, model_name, year, day, part, timed_out, puzzle_instructions)
    if prompt_result[0] == 'error':
        print(f"Error creating prompt: {prompt_result[1]}")
        return
    else:
        full_prompt = prompt_result[1]

    # Generate program
    program_result = aoc_api.generate_program(model_family, model_name, full_prompt, year, day, part)
    if program_result[0] == 'error':
        print(f"Error generating program: {program_result[1]}")
        if not existing_experiment:
            cursor.execute("""
                INSERT INTO experiments (model_family, model_name, year, day, part, prompt, status, result, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, 'error', ?, ?)
            """, (model_family, model_name, year, day, part, full_prompt, program_result[1], datetime.datetime.now()))
            conn.commit()
        else:
            update_experiment(conn, experiment_id, 'error', program_result[1], None, None, False, None)
        return
    elif program_result[0] == 'quota':
        print(f"Quota exhausted for {model_family}: {program_result[1]}")
        add_quota_timeout(conn, model_family)
        if not existing_experiment:
            cursor.execute("""
                INSERT INTO experiments (model_family, model_name, year, day, part, prompt, status, result, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, 'quota', ?, ?)
            """, (model_family, model_name, year, day, part, full_prompt, program_result[1], datetime.datetime.now()))
            conn.commit()
        else:
            update_experiment(conn, experiment_id, 'quota', program_result[1], None, None, False, None)
        return
    else:
        generated_program = program_result[1]

    # Run program
    run_result = aoc_api.run_program(year, day, part, generated_program, timeout)
    if run_result[0] == 'error':
        print(f"Error running program: {run_result[1]}")
        if not existing_experiment:
            cursor.execute("""
                INSERT INTO experiments (model_family, model_name, year, day, part, prompt, program, status, result, timeout, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'error', ?, ?, ?)
            """, (model_family, model_name, year, day, part, full_prompt, generated_program, run_result[1], timeout, datetime.datetime.now()))
            conn.commit()
        else:
            update_experiment(conn, experiment_id, 'error', run_result[1], None, None, False, timeout)
        return
    elif run_result[0] == 'timeout':
        print(f"Program timed out after {run_result[1]} seconds")
        timed_out = True
        if not existing_experiment:
            cursor.execute("""
                INSERT INTO experiments (model_family, model_name, year, day, part, prompt, program, status, result, timed_out, timeout, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'timeout', ?, ?, ?, ?)
            """, (model_family, model_name, year, day, part, full_prompt, generated_program, run_result[1], timed_out, timeout, datetime.datetime.now()))
            conn.commit()
        else:
            update_experiment(conn, experiment_id, 'timeout', str(run_result[1]), None, None, timed_out, timeout)
        return
    else:
        answer = run_result[1]
        is_correct = aoc_api.check_answer(year, day, part, answer)
        print(f"Answer: {answer}, Correct: {is_correct}")

        if not existing_experiment:
            cursor.execute("""
                INSERT INTO experiments (model_family, model_name, year, day, part, prompt, program, status, answer, correct, timeout, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'answer', ?, ?, ?, ?)
            """, (model_family, model_name, year, day, part, full_prompt, generated_program, answer, is_correct, timeout, datetime.datetime.now()))
            conn.commit()
        else:
            update_experiment(conn, experiment_id, 'answer', None, answer, is_correct, False, timeout)
            
        if is_correct:
            mark_puzzle_solved(conn, year, day, part)

def initialize_database(conn):
    """Initializes the database with model families, models, and puzzles."""
    cursor = conn.cursor()

    # Insert model families
    for family in aoc_api.modelfamilies():
        cursor.execute("INSERT OR IGNORE INTO model_families (name) VALUES (?)", (family,))

    # Insert models
    for family in aoc_api.modelfamilies():
        for model in aoc_api.models(family):
            cursor.execute("INSERT OR IGNORE INTO models (family, name) VALUES (?, ?)", (family, model))

    # Insert puzzles (example years 2015-2024)
    for year in range(2015, 2025):
        for day in range(1, 26):
            for part in range(1, 3):
                cursor.execute("INSERT OR IGNORE INTO puzzles (year, day, part) VALUES (?, ?, ?)", (year, day, part))

    conn.commit()

def main():
    """Main function for the experiment runner."""
    conn = sqlite3.connect(DATABASE)
    initialize_database(conn)

    while True:
        next_puzzle = get_next_puzzle_to_solve(conn)
        if not next_puzzle:
            print("All puzzles solved!")
            break

        year, day, part = next_puzzle
        models_data = get_models_to_test(conn)
        
        experiment_run = False
        for model_family, models in models_data.items():
            if is_quota_active(conn, model_family):
                continue  # Skip model family if quota is active

            for model_name in models:
                print(f"Running experiment for {model_family}/{model_name} on {year}/{day}/{part}")
                run_experiment(conn, model_family, model_name, year, day, part)
                experiment_run = True

        if not experiment_run:
            print("All model family quotas are active. Waiting...")
            time.sleep(60)  # Wait for 1 minute before checking again
        else:
            time.sleep(5) # Wait 5 seconds before running the next experiment

    conn.close()

if __name__ == "__main__":
    main()
