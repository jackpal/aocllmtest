import sqlite3
import time
import datetime
from aoc_api import *
from db_util import create_or_open_puzzle_db

def run_experiment():
    """Runs the experiment, iterating through puzzles and models."""
    conn = create_or_open_puzzle_db()
    cursor = conn.cursor()

    while True:
        model_family_to_run = None

        # Check for quota timeouts
        cursor.execute("SELECT model_family FROM QuotaTimeouts WHERE timeout_until > ?", (datetime.datetime.now(),))
        timed_out_families = [row[0] for row in cursor.fetchall()]

        available_model_families = [mf for mf in model_families() if mf not in timed_out_families]

        if not available_model_families:
            # If all model families are timed out, find the one with the shortest remaining timeout
            cursor.execute("SELECT model_family, MIN(timeout_until) FROM QuotaTimeouts")
            model_family, next_available_time = cursor.fetchone()
            sleep_duration = (next_available_time - datetime.datetime.now()).total_seconds()
            print(f"All model families are timed out. Waiting for {model_family} to be available again in {sleep_duration:.0f} seconds.")
            time.sleep(sleep_duration)
            continue

        # Select the next puzzle to solve
        # Find the latest solved puzzle
        cursor.execute("""
            SELECT puzzle_year, puzzle_day, puzzle_part
            FROM Experiments
            WHERE answer_is_correct = 1
            ORDER BY puzzle_year DESC, puzzle_day DESC, puzzle_part DESC
            LIMIT 1
        """)
        latest_solved = cursor.fetchone()

        if latest_solved:
            latest_year, latest_day, latest_part = latest_solved
        else:
            latest_year, latest_day, latest_part = 2024, 0, 0  # Start from the end 2024, day 0, part 0

        if latest_part == 1 and latest_day < 25:
            next_puzzle = (latest_year, latest_day, 2)
        elif latest_day < 24:
            next_puzzle = (latest_year, latest_day + 1, 1)
        elif latest_year > 2015:
            next_puzzle = (latest_year - 1, 1, 1)
        else:
            print("All puzzles have been attempted.")
            time.sleep(60)
            continue

        puzzle_year, puzzle_day, puzzle_part = next_puzzle
        print(f"Attempting puzzle {puzzle_year}/{puzzle_day}/{puzzle_part}")
        
        # Prioritize models that haven't been tried yet for this puzzle
        cursor.execute("""
            SELECT model_family, model_name
            FROM (
                SELECT m.model_family, m.model_name,
                       CASE WHEN e.experiment_id IS NULL THEN 0 ELSE 1 END as tried
                FROM (
                    SELECT DISTINCT model_family, model_name
                    FROM (
                        SELECT model_family, model_name FROM (
                            SELECT model_family, model as model_name
                            FROM (SELECT DISTINCT model_family FROM ModelFamilyRank), UNNEST(models(model_family)) AS model
                        )
                    )
                ) m
                LEFT JOIN Experiments e
                ON m.model_family = e.model_family
                AND m.model_name = e.model_name
                AND e.puzzle_year = ?
                AND e.puzzle_day = ?
                AND e.puzzle_part = ?
            )
            WHERE model_family IN (%s)
            ORDER BY tried, model_family, model_name
        """ % ','.join('?'*len(available_model_families)), (puzzle_year, puzzle_day, puzzle_part) + tuple(available_model_families))

        models_to_try = cursor.fetchall()

        if not models_to_try:
            print(f"All models for puzzle {puzzle_year}/{puzzle_day}/{puzzle_part} have been tried.")
            continue

        model_family, model_name = models_to_try[0]

        for timeout in [10, 100, 1000]:
            previous_attempt_timed_out = timeout > 10
            instructions_result = puzzle_instructions(puzzle_year, puzzle_day, puzzle_part)

            if instructions_result[0] == 'error':
                print(f"Error getting instructions: {instructions_result[1]}")
                continue
            elif instructions_result[0] == 'sequence':
                print(f"Need to solve {instructions_result[1]} first")
                continue
            elif instructions_result[0] == 'success':
                instructions = instructions_result[1]

            prompt_result = create_prompt(
                model_family, model_name, puzzle_year, puzzle_day, puzzle_part,
                previous_attempt_timed_out, instructions
            )

            if prompt_result[0] == 'error':
                print(f"Error creating prompt: {prompt_result[1]}")
                continue
            elif prompt_result[0] == 'success':
                full_prompt = prompt_result[1]

            cursor.execute("""
                INSERT OR IGNORE INTO Experiments (
                    model_family, model_name, puzzle_year, puzzle_day, puzzle_part,
                    prompt, experiment_started_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (model_family, model_name, puzzle_year, puzzle_day, puzzle_part, full_prompt, datetime.datetime.now()))
            conn.commit()

            print(f"Running experiment for {model_family}/{model_name} on {puzzle_year}/{puzzle_day}/{puzzle_part} with timeout {timeout}")

            generate_result = generate_program(
                model_family, model_name, full_prompt, puzzle_year, puzzle_day, puzzle_part
            )

            if generate_result[0] == 'error':
                print(f"Error generating program: {generate_result[1]}")
                cursor.execute("""
                    UPDATE Experiments
                    SET run_status = 'error', run_error_message = ?, experiment_finished_at = ?
                    WHERE model_family = ? AND model_name = ? AND puzzle_year = ? AND puzzle_day = ? AND puzzle_part = ?
                """, (generate_result[1], datetime.datetime.now(), model_family, model_name, puzzle_year, puzzle_day, puzzle_part))
                conn.commit()
                continue
            elif generate_result[0] == 'quota':
                print(f"Quota exhausted for {model_family}: {generate_result[1]}")
                cursor.execute("INSERT OR REPLACE INTO QuotaTimeouts (model_family, timeout_until) VALUES (?, ?)",
                               (model_family, datetime.datetime.now() + datetime.timedelta(hours=1)))
                conn.commit()
                break # Exit the timeout loop
            elif generate_result[0] == 'success':
                program = generate_result[1]

            cursor.execute("""
                UPDATE Experiments
                SET program = ?
                WHERE model_family = ? AND model_name = ? AND puzzle_year = ? AND puzzle_day = ? AND puzzle_part = ?
            """, (program, model_family, model_name, puzzle_year, puzzle_day, puzzle_part))
            conn.commit()

            run_result = run_program(puzzle_year, puzzle_day, puzzle_part, program, timeout)

            if run_result[0] == 'error':
                print(f"Error running program: {run_result[1]}")
                cursor.execute("""
                    UPDATE Experiments
                    SET run_status = 'error', run_error_message = ?, experiment_finished_at = ?
                    WHERE model_family = ? AND model_name = ? AND puzzle_year = ? AND puzzle_day = ? AND puzzle_part = ?
                """, (run_result[1], datetime.datetime.now(), model_family, model_name, puzzle_year, puzzle_day, puzzle_part))
                conn.commit()
                continue
            elif run_result[0] == 'timeout':
                print(f"Program timed out after {run_result[1]} seconds")
                cursor.execute("""
                    UPDATE Experiments
                    SET run_status = 'timeout', run_timeout_seconds = ?, experiment_finished_at = ?
                    WHERE model_family = ? AND model_name = ? AND puzzle_year = ? AND puzzle_day = ? AND puzzle_part = ?
                """, (run_result[1], datetime.datetime.now(), model_family, model_name, puzzle_year, puzzle_day, puzzle_part))
                conn.commit()
                if timeout == 1000:
                    break  # Give up on this model/puzzle combination after the longest timeout
                else:
                    continue # Try again with a longer timeout
            elif run_result[0] == 'answer':
                answer = run_result[1]
                is_correct = check_answer(puzzle_year, puzzle_day, puzzle_part, answer)
                print(f"Answer: {answer}, Correct: {is_correct}")
                cursor.execute("""
                    UPDATE Experiments
                    SET run_status = 'answer', answer = ?, answer_is_correct = ?, experiment_finished_at = ?
                    WHERE model_family = ? AND model_name = ? AND puzzle_year = ? AND puzzle_day = ? AND puzzle_part = ?
                """, (answer, is_correct, datetime.datetime.now(), model_family, model_name, puzzle_year, puzzle_day, puzzle_part))
                conn.commit()
                break  # Move on to the next model after getting an answer

        # Update the ranking tables after each puzzle attempt
        update_ranking_tables(conn)
        
def update_ranking_tables(conn):
    """Updates the ModelRank, ModelFamilyRank, and YearRank tables based on experiment results."""
    cursor = conn.cursor()

    # Update ModelRank
    cursor.execute("""
        INSERT OR REPLACE INTO ModelRank (model_family, model_name, solved_count, total_attempted, success_rate)
        SELECT
            model_family,
            model_name,
            SUM(CASE WHEN answer_is_correct = 1 THEN 1 ELSE 0 END) as solved_count,
            COUNT(*) as total_attempted,
            CAST(SUM(CASE WHEN answer_is_correct = 1 THEN 1 ELSE 0 END) AS REAL) / COUNT(*) as success_rate
        FROM Experiments
        GROUP BY model_family, model_name
    """)

    # Update ModelFamilyRank
    cursor.execute("""
        INSERT OR REPLACE INTO ModelFamilyRank (model_family, solved_count, total_attempted, success_rate)
        SELECT
            model_family,
            SUM(CASE WHEN answer_is_correct = 1 THEN 1 ELSE 0 END) as solved_count,
            COUNT(*) as total_attempted,
            CAST(SUM(CASE WHEN answer_is_correct = 1 THEN 1 ELSE 0 END) AS REAL) / COUNT(*) as success_rate
        FROM Experiments
        GROUP BY model_family
    """)

    # Update YearRank
    cursor.execute("""
        INSERT OR REPLACE INTO YearRank (puzzle_year, solved_count, total_attempted, success_rate)
        SELECT
            puzzle_year,
            SUM(CASE WHEN answer_is_correct = 1 THEN 1 ELSE 0 END) as solved_count,
            COUNT(*) as total_attempted,
            CAST(SUM(CASE WHEN answer_is_correct = 1 THEN 1 ELSE 0 END) AS REAL) / COUNT(*) as success_rate
        FROM Experiments
        GROUP BY puzzle_year
    """)

    conn.commit()
    
if __name__ == "__main__":
    run_experiment()
