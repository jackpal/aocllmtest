import sqlite3
import time
import datetime
from aoc_api import *
from db_util import create_or_open_puzzle_db

def get_next_puzzle_to_solve(cursor, timed_out_families):
    """
    Determines the next puzzle to solve based on the prioritization rules.
    Returns a tuple: (next_puzzle, more_puzzles_available)
      - next_puzzle: A tuple representing the next puzzle to solve, or None if no puzzles are available.
      - more_puzzles_available: A boolean indicating if there are more puzzles to solve, even if
        they are currently blocked by timeouts.
    """
    cursor.execute("""
        SELECT
            e.puzzle_year,
            e.puzzle_day,
            e.puzzle_part,
            e.model_family,
            e.model_name
        FROM
            Experiments e
        WHERE
            e.answer_is_correct = 1
        ORDER BY
            e.puzzle_year DESC,
            e.puzzle_day DESC,
            e.puzzle_part DESC
        LIMIT 1
    """)
    latest_solved = cursor.fetchone()

    if latest_solved:
        latest_year, latest_day, latest_part, _, _ = latest_solved
    else:
        latest_year, latest_day, latest_part = 2024, 0, 0

    # Construct the query with timed-out families excluded
    timed_out_placeholders = ','.join(['?'] * len(timed_out_families))

    # Use f-string to safely incorporate the placeholders into the query
    query = f"""
        WITH generate_series(value) AS (
            SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL
            SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL
            SELECT 9 UNION ALL SELECT 10 UNION ALL SELECT 11 UNION ALL SELECT 12 UNION ALL
            SELECT 13 UNION ALL SELECT 14 UNION ALL SELECT 15 UNION ALL SELECT 16 UNION ALL
            SELECT 17 UNION ALL SELECT 18 UNION ALL SELECT 19 UNION ALL SELECT 20 UNION ALL
            SELECT 21 UNION ALL SELECT 22 UNION ALL SELECT 23 UNION ALL SELECT 24 UNION ALL
            SELECT 25
        ), ValidExperiments AS (
            SELECT DISTINCT
                e.puzzle_year,
                e.puzzle_day,
                e.model_family,
                e.model_name
            FROM
                Experiments e
            WHERE
                e.puzzle_part = 1 AND e.answer_is_correct = 1
        )
        SELECT
            m.model_family, m.model_name, y.puzzle_year, d.puzzle_day, p.puzzle_part
        FROM
            Models m
        CROSS JOIN (
            SELECT DISTINCT puzzle_year FROM (
                SELECT puzzle_year FROM Experiments
                UNION ALL
                SELECT 2015 AS puzzle_year
                UNION ALL
                SELECT 2016 AS puzzle_year
                UNION ALL
                SELECT 2017 AS puzzle_year
                UNION ALL
                SELECT 2018 AS puzzle_year
                UNION ALL
                SELECT 2019 AS puzzle_year
                UNION ALL
                SELECT 2020 AS puzzle_year
                UNION ALL
                SELECT 2021 AS puzzle_year
                UNION ALL
                SELECT 2022 AS puzzle_year
                UNION ALL
                SELECT 2023 AS puzzle_year
                UNION ALL
                SELECT 2024 AS puzzle_year
            )
        ) y
        CROSS JOIN (
            SELECT DISTINCT puzzle_day FROM (
                SELECT puzzle_day FROM Experiments
                UNION ALL
                SELECT value AS puzzle_day FROM generate_series
            )
        ) d
        CROSS JOIN (
            SELECT DISTINCT puzzle_part FROM (
                SELECT puzzle_part FROM Experiments
                UNION
                SELECT 1 AS puzzle_part
                UNION
                SELECT 2 AS puzzle_part
            )
        ) p
        LEFT JOIN
            Experiments e ON m.model_family = e.model_family
            AND m.model_name = e.model_name
            AND y.puzzle_year = e.puzzle_year
            AND d.puzzle_day = e.puzzle_day
            AND p.puzzle_part = e.puzzle_part
        WHERE e.experiment_id IS NULL
        AND NOT (d.puzzle_day = 25 AND p.puzzle_part = 2)
        AND (p.puzzle_part = 1 OR EXISTS (
            SELECT 1
            FROM ValidExperiments ve
            WHERE ve.model_family = m.model_family
            AND ve.model_name = m.model_name
            AND ve.puzzle_year = y.puzzle_year
            AND ve.puzzle_day = d.puzzle_day
        ))
        AND m.model_family NOT IN ({timed_out_placeholders})
        LIMIT 1
    """

    # Execute the query, passing in the timed_out_families list
    cursor.execute(query, timed_out_families)

    next_puzzle = cursor.fetchone()

    # Check if there are any more puzzles left to solve, even if some are blocked by timeouts
    cursor.execute(f"""
        WITH generate_series(value) AS (
            SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL
            SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL
            SELECT 9 UNION ALL SELECT 10 UNION ALL SELECT 11 UNION ALL SELECT 12 UNION ALL
            SELECT 13 UNION ALL SELECT 14 UNION ALL SELECT 15 UNION ALL SELECT 16 UNION ALL
            SELECT 17 UNION ALL SELECT 18 UNION ALL SELECT 19 UNION ALL SELECT 20 UNION ALL
            SELECT 21 UNION ALL SELECT 22 UNION ALL SELECT 23 UNION ALL SELECT 24 UNION ALL
            SELECT 25
        ), ValidExperiments AS (
            SELECT DISTINCT
                e.puzzle_year,
                e.puzzle_day,
                e.model_family,
                e.model_name
            FROM
                Experiments e
            WHERE
                e.puzzle_part = 1 AND e.answer_is_correct = 1
        )
        SELECT 1
        FROM
            Models m
        CROSS JOIN (
            SELECT DISTINCT puzzle_year FROM (
                SELECT puzzle_year FROM Experiments
                UNION ALL
                SELECT 2015 AS puzzle_year
                UNION ALL
                SELECT 2016 AS puzzle_year
                UNION ALL
                SELECT 2017 AS puzzle_year
                UNION ALL
                SELECT 2018 AS puzzle_year
                UNION ALL
                SELECT 2019 AS puzzle_year
                UNION ALL
                SELECT 2020 AS puzzle_year
                UNION ALL
                SELECT 2021 AS puzzle_year
                UNION ALL
                SELECT 2022 AS puzzle_year
                UNION ALL
                SELECT 2023 AS puzzle_year
                UNION ALL
                SELECT 2024 AS puzzle_year
            )
        ) y
        CROSS JOIN (
            SELECT DISTINCT puzzle_day FROM (
                SELECT puzzle_day FROM Experiments
                UNION ALL
                SELECT value AS puzzle_day FROM generate_series
            )
        ) d
        CROSS JOIN (
            SELECT DISTINCT puzzle_part FROM (
                SELECT puzzle_part FROM Experiments
                UNION
                SELECT 1 AS puzzle_part
                UNION
                SELECT 2 AS puzzle_part
            )
        ) p
        LEFT JOIN
            Experiments e ON m.model_family = e.model_family
            AND m.model_name = e.model_name
            AND y.puzzle_year = e.puzzle_year
            AND d.puzzle_day = e.puzzle_day
            AND p.puzzle_part = e.puzzle_part
        WHERE e.experiment_id IS NULL
        AND NOT (d.puzzle_day = 25 AND p.puzzle_part = 2)
        AND (p.puzzle_part = 1 OR EXISTS (
            SELECT 1
            FROM ValidExperiments ve
            WHERE ve.model_family = m.model_family
            AND ve.model_name = m.model_name
            AND ve.puzzle_year = y.puzzle_year
            AND ve.puzzle_day = d.puzzle_day
        ))
        LIMIT 1
    """)
    more_puzzles_available = cursor.fetchone() is not None

    if next_puzzle:
        model_family, model_name, puzzle_year, puzzle_day, puzzle_part = next_puzzle
        return (puzzle_year, puzzle_day, puzzle_part, model_family, model_name), more_puzzles_available
    else:
        return None, more_puzzles_available  # Indicates no more puzzles to solve right now
    
def run_experiment_for_puzzle(puzzle_year, puzzle_day, puzzle_part, model_family, model_name):
    """Runs the experiment for a single puzzle."""
    conn = create_or_open_puzzle_db()
    cursor = conn.cursor()

    for timeout in [10, 100]:
        previous_attempt_timed_out = timeout > 10
        instructions_result = puzzle_instructions(puzzle_year, puzzle_day, puzzle_part)

        if instructions_result[0] == 'error':
            print(f"Error getting instructions: {instructions_result[1]}")
            break  # Exit timeout loop, move on to next puzzle
        elif instructions_result[0] == 'sequence':
            print(f"Need to solve {instructions_result[1]} first")
            break  # Exit timeout loop, move on to next puzzle
        elif instructions_result[0] == 'success':
            instructions = instructions_result[1]

        prompt_result = create_prompt(
            model_family, model_name, puzzle_year, puzzle_day, puzzle_part,
            previous_attempt_timed_out, instructions
        )

        if prompt_result[0] == 'error':
            print(f"Error creating prompt: {prompt_result[1]}")
            break  # Exit timeout loop, move on to next puzzle
        elif prompt_result[0] == 'success':
            full_prompt = prompt_result[1]

        print(f"Running experiment for {model_family}/{model_name} on {puzzle_year}/{puzzle_day}/{puzzle_part} with timeout {timeout}")

        generate_result = generate_program(
            model_family, model_name, full_prompt, puzzle_year, puzzle_day, puzzle_part
        )

        if generate_result[0] == 'quota':
            print(f"Quota exhausted for {model_family}: {generate_result[1]}")
            # We should not insert a row into Experiments here
            # because we have not yet generated a program.
            conn.close()
            return 'quota_error'
        elif generate_result[0] == 'error':
            print(f"Error generating program: {generate_result[1]}")
            # We should not insert a row into Experiments here
            # because we have not yet generated a program.
            break  # Exit timeout loop, move on to next puzzle
        elif generate_result[0] == 'success':
            program = generate_result[1]

        # Insert experiment record *after* successful program generation
        cursor.execute("""
            INSERT OR IGNORE INTO Experiments (
                model_family, model_name, puzzle_year, puzzle_day, puzzle_part,
                prompt, program, experiment_started_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (model_family, model_name, puzzle_year, puzzle_day, puzzle_part, full_prompt, program, datetime.datetime.now()))
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
            break  # Exit timeout loop, move on to next puzzle with this model
        elif run_result[0] == 'timeout':
            print(f"Program timed out after {run_result[1]} seconds")
            cursor.execute("""
                UPDATE Experiments
                SET run_status = 'timeout', run_timeout_seconds = ?, experiment_finished_at = ?
                WHERE model_family = ? AND model_name = ? AND puzzle_year = ? AND puzzle_day = ? AND puzzle_part = ?
            """, (run_result[1], datetime.datetime.now(), model_family, model_name, puzzle_year, puzzle_day, puzzle_part))
            conn.commit()
            if timeout == 100:
                break  # Give up on this model/puzzle combination after the longest timeout
            else:
                continue  # Try again with a longer timeout
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

    conn.close()
    return 'success' # Indicate that the experiment completed (or was skipped)

def run_experiment():
    """Runs the experiment, processing one puzzle at a time."""
    conn = create_or_open_puzzle_db()
    cursor = conn.cursor()

    while True:
        # Check for quota timeouts for all model families
        cursor.execute("SELECT model_family FROM QuotaTimeouts WHERE timeout_until > ?", (datetime.datetime.now(),))
        timed_out_families = [row[0] for row in cursor.fetchall()]

        # Get the next puzzle to solve
        next_puzzle, more_puzzles_available = get_next_puzzle_to_solve(cursor, timed_out_families)

        if next_puzzle is None:
            if not more_puzzles_available:
                print("All puzzles have been attempted.")
                break  # Exit the loop if no more puzzles
            else:
                # Find the earliest timeout expiry among timed-out families.
                cursor.execute("SELECT MIN(timeout_until) FROM QuotaTimeouts")
                next_available_time_str = cursor.fetchone()[0]

                if next_available_time_str is not None:
                    # Convert the string to a datetime object.
                    next_available_time = datetime.datetime.fromisoformat(next_available_time_str)

                    # Calculate sleep duration based on the earliest timeout.
                    sleep_duration = max(0, (next_available_time - datetime.datetime.now()).total_seconds())
                    print(f"All model families are timed out. Sleeping for {sleep_duration:.0f} seconds (until {next_available_time}).")
                    time.sleep(sleep_duration)
                    continue
                else:
                    print("Warning: Could not determine the next available time. Retrying after a short delay.")
                    time.sleep(60)
                    continue

        puzzle_year, puzzle_day, puzzle_part, model_family, model_name = next_puzzle

        # Run the experiment for the selected puzzle
        print(f"Attempting puzzle {puzzle_year}/{puzzle_day}/{puzzle_part} with model {model_family}/{model_name}")
        result = run_experiment_for_puzzle(puzzle_year, puzzle_day, puzzle_part, model_family, model_name)

        # If a quota error occurred, handle it
        if result == 'quota_error':
            print(f"Quota exhausted for {model_family}. Recording timeout and skipping.")
            cursor.execute("INSERT OR REPLACE INTO QuotaTimeouts (model_family, timeout_until) VALUES (?, ?)",
                           (model_family, datetime.datetime.now() + datetime.timedelta(hours=1)))
            conn.commit()
            # Don't continue here, so we can update ranking tables

        # Update the ranking tables after each puzzle attempt
        update_ranking_tables(conn)

    conn.close()
        
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
