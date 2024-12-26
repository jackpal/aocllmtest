import sqlite3
import time
import csv
from typing import List, Tuple, Optional
import argparse
from flask import Flask, jsonify, render_template
import aoc_api  # Assuming aoc_api.py contains the provided functions

app = Flask(__name__)

DATABASE_NAME = "aoc_results.db"

# --- Database Initialization and Helper Functions ---

def initialize_database():
    """Creates the necessary tables in the SQLite database."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS experiments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_family TEXT,
            model_name TEXT,
            puzzle_year INTEGER,
            puzzle_day INTEGER,
            puzzle_part INTEGER,
            prompt TEXT,
            program TEXT,
            result TEXT,
            answer TEXT,
            correct BOOLEAN,
            timeout INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            generate_program_status TEXT,
            generate_program_message TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quota_limits (
            model_family TEXT PRIMARY KEY,
            blocked_until DATETIME
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS puzzle_prose (
            puzzle_year INTEGER,
            puzzle_day INTEGER,
            puzzle_part INTEGER,
            prose TEXT,
            PRIMARY KEY (puzzle_year, puzzle_day, puzzle_part)
        )
    """)

    conn.commit()
    conn.close()

def get_puzzle_prose(year: int, day: int, part: int) -> str:
    """Retrieves puzzle prose from the database."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT prose FROM puzzle_prose WHERE puzzle_year = ? AND puzzle_day = ? AND puzzle_part = ?", (year, day, part))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def store_puzzle_prose(year: int, day: int, part: int, prose: str):
    """Stores puzzle prose in the database."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO puzzle_prose (puzzle_year, puzzle_day, puzzle_part, prose) VALUES (?, ?, ?, ?)", (year, day, part, prose))
    conn.commit()
    conn.close()

def get_next_experiment() -> Optional[Tuple[str, str, int, int, int, int]]:
    """
    Determines the next experiment to run based on the defined strategies.

    Returns:
        A tuple representing the next experiment (model_family, model_name, year, day, part, timeout),
        or None if no suitable experiment is found.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Check for quota limits
    cursor.execute("SELECT model_family FROM quota_limits WHERE blocked_until > ?", (time.time(),))
    blocked_families = [row[0] for row in cursor.fetchall()]

    # Strategy: Prioritize recent years, lower days, and then iterate through model families and models
    for year in range(2024, 2014, -1):  # 2024 down to 2015
        for day in range(1, 26):
            for part in range(1, 3):
                if day == 25 and part == 2:
                    continue # Day 25 part 2 is not a real puzzle

                # Check if part 1 is solved before trying part 2
                if part == 2:
                    cursor.execute("""
                        SELECT COUNT(*) FROM experiments
                        WHERE puzzle_year = ? AND puzzle_day = ? AND puzzle_part = 1 AND correct = TRUE
                    """, (year, day))
                    if cursor.fetchone()[0] == 0:
                        continue  # Part 1 not solved, skip part 2

                for model_family in aoc_api.model_families():
                    if model_family in blocked_families:
                        continue  # Skip families with active quota limits

                    for model_name in aoc_api.models(model_family):
                        # Check if this experiment has already been completed successfully
                        cursor.execute("""
                            SELECT COUNT(*) FROM experiments
                            WHERE model_family = ? AND model_name = ? AND puzzle_year = ? AND puzzle_day = ? AND puzzle_part = ? AND correct = TRUE
                        """, (model_family, model_name, year, day, part))
                        if cursor.fetchone()[0] > 0:
                            continue

                        # Check for previous timeouts and adjust timeout accordingly
                        cursor.execute("""
                            SELECT MAX(timeout) FROM experiments
                            WHERE model_family = ? AND model_name = ? AND puzzle_year = ? AND puzzle_day = ? AND puzzle_part = ? AND result = 'timeout'
                        """, (model_family, model_name, year, day, part))
                        previous_timeout = cursor.fetchone()[0]

                        if previous_timeout is None:
                            timeout = 10
                        elif previous_timeout == 10:
                            timeout = 100
                        elif previous_timeout == 100:
                            timeout = 1000
                        else:
                            timeout = None  # Already tried all timeouts

                        if timeout is not None:
                            conn.close()
                            return model_family, model_name, year, day, part, timeout
    conn.close()
    return None  # No more experiments to run

def record_experiment(model_family: str, model_name: str, year: int, day: int, part: int, prompt: str, program: str, result: str, answer: Optional[str], correct: Optional[bool], timeout: int, generate_program_status: str, generate_program_message: str):
    """Records the results of an experiment in the database."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO experiments (model_family, model_name, puzzle_year, puzzle_day, puzzle_part, prompt, program, result, answer, correct, timeout, generate_program_status, generate_program_message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (model_family, model_name, year, day, part, prompt, program, result, answer, correct, timeout, generate_program_status, generate_program_message))

    conn.commit()
    conn.close()

def update_quota_limit(model_family: str, blocked_until: Optional[float]):
    """Updates the quota limit for a given model family."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    if blocked_until is None:
        cursor.execute("DELETE FROM quota_limits WHERE model_family = ?", (model_family,))
    else:
        cursor.execute("INSERT OR REPLACE INTO quota_limits (model_family, blocked_until) VALUES (?, ?)", (model_family, blocked_until))

    conn.commit()
    conn.close()

# --- Main Logic ---

def run_experiments():
    """Runs the main loop for conducting experiments."""
    while True:
        next_experiment = get_next_experiment()
        if next_experiment is None:
            print("No more experiments to run at this time.")
            break

        model_family, model_name, year, day, part, timeout = next_experiment
        print(f"Running experiment: {model_family} {model_name}, Year {year}, Day {day}, Part {part}, Timeout {timeout}")
        
        # Try to get the puzzle prose from the database.
        puzzle_prose = get_puzzle_prose(year, day, part)
        if puzzle_prose is None:
            # We don't have the puzzle prose yet. Try to get it by solving a previous puzzle.
            if part == 1:
                print(f"Error: don't have puzzle prose for year {year} day {day} part {part}, and there is no previous puzzle to solve.")
                continue
            
            previous_part = part - 1
            
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM experiments
                WHERE puzzle_year = ? AND puzzle_day = ? AND puzzle_part = ? AND correct = TRUE
            """, (year, day, previous_part))
            
            if cursor.fetchone()[0] == 0:
                print(f"Error: don't have puzzle prose for year {year} day {day} part {part}, and previous puzzle part {previous_part} has not been solved yet.")
                conn.close()
                continue
            else:
                print(f"Error: don't have puzzle prose for year {year} day {day} part {part}, and that is unexpected because the previous puzzle part {previous_part} has been solved.")
                conn.close()
                continue
        
        # Check if the last attempt timed out
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*)
            FROM experiments
            WHERE model_family = ? AND model_name = ? AND puzzle_year = ? AND puzzle_day = ? AND puzzle_part = ? AND result = 'timeout'
        """, (model_family, model_name, year, day, part))
        previous_attempt_timed_out = cursor.fetchone()[0] > 0
        conn.close()

        # Create the prompt
        prompt_status, prompt_data = aoc_api.create_prompt(model_family, model_name, year, day, part, puzzle_prose, previous_attempt_timed_out)

        if prompt_status == 'error':
            print(f"Error creating prompt: {prompt_data}")
            record_experiment(model_family, model_name, year, day, part, None, None, 'error', None, None, timeout, 'error', prompt_data)
            continue
        elif prompt_status == 'sequence':
            print(f"Prompt creation says another puzzle needs to be solved first: {prompt_data}")
            record_experiment(model_family, model_name, year, day, part, None, None, 'sequence', None, None, timeout, 'sequence', prompt_data)
            continue
            
        prompt = prompt_data

        # Generate the program
        generate_status, generate_data = aoc_api.generate_program(model_family, model_name, prompt, year, day, part)

        if generate_status == 'error':
            print(f"Error generating program: {generate_data}")
            record_experiment(model_family, model_name, year, day, part, prompt, None, 'error', None, None, timeout, 'error', generate_data)
            continue
        elif generate_status == 'quota':
            print(f"Quota limit reached for {model_family}: {generate_data}")
            record_experiment(model_family, model_name, year, day, part, prompt, None, 'quota', None, None, timeout, 'quota', generate_data)
            update_quota_limit(model_family, time.time() + 3600)  # Block for 1 hour
            continue
        else:
            program = generate_data
            update_quota_limit(model_family, None)

        # Run the program
        run_status, run_data = aoc_api.run_program(program, timeout)

        if run_status == 'error':
            print(f"Error running program: {run_data}")
            record_experiment(model_family, model_name, year, day, part, prompt, program, 'error', None, None, timeout, generate_status, generate_data)
            continue
        elif run_status == 'timeout':
            print(f"Program timed out after {run_data} seconds")
            record_experiment(model_family, model_name, year, day, part, prompt, program, 'timeout', None, None, timeout, generate_status, generate_data)
            continue
        else:
            answer = run_data
            
            # Check the answer
            correct = aoc_api.check_answer(year, day, part, answer)
            print(f"Program output: {answer}, Correct: {correct}")

            record_experiment(model_family, model_name, year, day, part, prompt, program, 'success', answer, correct, timeout, generate_status, generate_data)

        time.sleep(1)  # Be nice to the APIs

# --- Query and Reporting Functions ---

def total_experiments_count() -> Tuple[int, int]:
    """Calculates the total number of experiments run and the number of experiments remaining."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM experiments")
    total_run = cursor.fetchone()[0]

    total_possible = 0
    for year in range(2015, 2025):
        for day in range(1, 26):
            for part in range(1, 3):
                if day == 25 and part == 2:
                    continue
                
                for model_family in aoc_api.model_families():
                    for model_name in aoc_api.models(model_family):
                        total_possible += 1
    
    conn.close()
    return total_run, total_possible - total_run

def rank_model_families() -> List[Tuple[str, float]]:
    """Ranks model families by their success rate."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT model_family, AVG(correct) as success_rate
        FROM experiments
        WHERE result = 'success'
        GROUP BY model_family
        ORDER BY success_rate DESC
    """)
    results = cursor.fetchall()
    conn.close()
    return results

def rank_models_within_family(model_family: str) -> List[Tuple[str, float]]:
    """Ranks models within a given family by their success rate."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT model_name, AVG(correct) as success_rate
        FROM experiments
        WHERE model_family = ? AND result = 'success'
        GROUP BY model_name
        ORDER BY success_rate DESC
    """, (model_family,))
    results = cursor.fetchall()
    conn.close()
    return results

def rank_years_by_difficulty() -> List[Tuple[int, float]]:
    """Ranks puzzle years by their average difficulty (inverse of success rate)."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT puzzle_year, AVG(correct) as success_rate
        FROM experiments
        WHERE result = 'success'
        GROUP BY puzzle_year
        ORDER BY success_rate ASC
    """)
    results = cursor.fetchall()
    conn.close()
    return results

def generate_csv_report(filename: str):
    """Generates a CSV report of all experiment results."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM experiments")
    results = cursor.fetchall()
    conn.close()

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write header row
        writer.writerow([description[0] for description in cursor.description])
        # Write data rows
        writer.writerows(results)

# --- Flask API Endpoints ---

@app.route('/')
def index():
    """Provides a simple HTML interface to view experiment status and results."""
    total_run, total_remaining = total_experiments_count()
    model_family_ranks = rank_model_families()
    year_ranks = rank_years_by_difficulty()

    return render_template('index.html', total_run=total_run, total_remaining=total_remaining,
                           model_family_ranks=model_family_ranks, year_ranks=year_ranks)

@app.route('/api/status')
def api_status():
    """Provides API endpoint for getting the current experiment status."""
    total_run, total_remaining = total_experiments_count()
    return jsonify({'total_experiments_run': total_run, 'total_experiments_remaining': total_remaining})

@app.route('/api/rank/model_families')
def api_rank_model_families():
    """Provides API endpoint for getting the ranking of model families."""
    ranks = rank_model_families()
    return jsonify(ranks)

@app.route('/api/rank/models/<model_family>')
def api_rank_models_within_family(model_family):
    """Provides API endpoint for getting the ranking of models within a family."""
    ranks = rank_models_within_family(model_family)
    return jsonify(ranks)

@app.route('/api/rank/years')
def api_rank_years():
    """Provides API endpoint for getting the ranking of puzzle years by difficulty."""
    ranks = rank_years_by_difficulty()
    return jsonify(ranks)

# --- Command-Line Argument Parsing ---

def main():
    """Parses command-line arguments and either runs experiments or generates reports."""
    parser = argparse.ArgumentParser(description="Run experiments to test AI models on Advent of Code puzzles.")
    parser.add_argument('--run', action='store_true', help='Run the experiment loop.')
    parser.add_argument('--report', action='store_true', help='Generate a report.')
    parser.add_argument('--csv', metavar='FILENAME', help='Generate a CSV report and save it to the specified file.')
    parser.add_argument('--flask', action='store_true', help='Start the Flask web server for viewing results.')

    args = parser.parse_args()

    initialize_database()

    if args.run:
        run_experiments()

    if args.report:
        total_run, total_remaining = total_experiments_count()
        print(f"Total experiments run: {total_run}")
        print(f"Total experiments remaining: {total_remaining}")

        print("\nModel Family Rankings:")
        for family, success_rate in rank_model_families():
            print(f"  {family}: {success_rate:.2%}")

        print("\nYear Rankings by Difficulty (hardest to easiest):")
        for year, success_rate in rank_years_by_difficulty():
            print(f"  {year}: {success_rate:.2%}")

    if args.csv:
        generate_csv_report(args.csv)
        print(f"CSV report generated: {args.csv}")
    
    if args.flask:
        app.run(debug=True)

if __name__ == "__main__":
    main()