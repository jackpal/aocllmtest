import sqlite3
import time
import datetime
from aoc_api import *
from db_util import create_or_open_puzzle_db

def get_next_puzzle_to_solve(cursor):
    """
    Determines the next puzzle to solve based on the prioritization rules:
    1. Descending years
    2. Ascending days
    3. Ascending parts
    4. Ascending model families
    5. Ascending models
    Puzzles that have already been attempted are skipped.
    Day 25 Part 2 puzzles are skipped.
    For a given model, don't try to solve part 2 of a puzzle if the given model 
    has not been able to correctly answer part 1 of the puzzle.
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

    cursor.execute("""
        WITH generate_series(value) AS (
            SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL
            SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL
            SELECT 9 UNION ALL SELECT 10 UNION ALL SELECT 11 UNION ALL SELECT 12 UNION ALL
            SELECT 13 UNION ALL SELECT 14 UNION ALL SELECT 15 UNION ALL SELECT 16 UNION ALL
            SELECT 17 UNION ALL SELECT 18 UNION ALL SELECT 19 UNION ALL SELECT 20 UNION ALL
            SELECT 21 UNION ALL SELECT 22 UNION ALL SELECT 23 UNION ALL SELECT 24 UNION ALL
            SELECT 25
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
        LEFT JOIN
            Experiments e1 ON m.model_family = e1.model_family
            AND m.model_name = e1.model_name
            AND y.puzzle_year = e1.puzzle_year
            AND d.puzzle_day = e1.puzzle_day
            AND e1.puzzle_part = 1
        WHERE e.experiment_id IS NULL
        AND NOT (d.puzzle_day = 25 AND p.puzzle_part = 2)
        AND (p.puzzle_part = 1 OR e1.answer_is_correct = 1)
        ORDER BY
            y.puzzle_year DESC,
            d.puzzle_day ASC,
            p.puzzle_part ASC,
            m.model_family ASC,
            m.model_name ASC
        LIMIT 1
    """)

    next_puzzle = cursor.fetchone()

    if next_puzzle:
        model_family, model_name, puzzle_year, puzzle_day, puzzle_part = next_puzzle
        return puzzle_year, puzzle_day, puzzle_part, model_family, model_name
    else:
        return None  # Indicates no more puzzles to solve

def run_experiment_for_puzzle(puzzle_year, puzzle_day, puzzle_part, model_family, model_name):
    """Runs the experiment for a single puzzle."""
    conn = create_or_open_puzzle_db()
    cursor = conn.cursor()

    for timeout in [10, 100]:
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
            conn.close()
            return  # Exit early on quota error
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
            break # Move on to the next model after an error
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

    conn.close()

def run_experiment():
    """Runs the experiment, processing one puzzle at a time."""
    conn = create_or_open_puzzle_db()
    cursor = conn.cursor()

    while True:
        # Check for quota timeouts for all model families
        cursor.execute("SELECT model_family FROM QuotaTimeouts WHERE timeout_until > ?", (datetime.datetime.now(),))
        timed_out_families = [row[0] for row in cursor.fetchall()]

        all_families_timed_out = set(timed_out_families) == set(model_families())

        if all_families_timed_out:
            # If all model families are timed out, find the one with the *earliest* timeout expiry
            cursor.execute("SELECT MIN(timeout_until) FROM QuotaTimeouts")
            next_available_time_str = cursor.fetchone()[0]

            if next_available_time_str is not None:
                # Convert the string to a datetime object
                next_available_time = datetime.datetime.fromisoformat(next_available_time_str)

                sleep_duration = max(0, (next_available_time - datetime.datetime.now()).total_seconds())
                print(f"All model families are timed out. Sleeping for {sleep_duration:.0f} seconds (until {next_available_time}).")
                time.sleep(sleep_duration)
                continue  # Skip puzzle submission and go to the next iteration
            else:
                print("Warning: No timeout information found, but all model families seem timed out. Retrying.")

        # Get the next puzzle to solve
        next_puzzle = get_next_puzzle_to_solve(cursor)
        if next_puzzle is None:
            print("All puzzles have been attempted.")
            break  # Exit the loop if no more puzzles

        puzzle_year, puzzle_day, puzzle_part, model_family, model_name = next_puzzle

        if model_family in timed_out_families:
            # If this model family is timed out, skip it for now
            print(f"Model family {model_family} is currently timed out. Skipping.")
            continue

        # Run the experiment for the selected puzzle
        print(f"Attempting puzzle {puzzle_year}/{puzzle_day}/{puzzle_part} with model {model_family}/{model_name}")
        run_experiment_for_puzzle(puzzle_year, puzzle_day, puzzle_part, model_family, model_name)

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
