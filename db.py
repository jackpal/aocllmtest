# db.py
import sqlite3
from typing import List, Tuple, Dict, Any

DATABASE_NAME = "aoc_results.db"

def create_tables() -> None:
    """Creates the necessary tables in the database."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS experiments (
            experiment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_family TEXT NOT NULL,
            model_name TEXT NOT NULL,
            puzzle_year INTEGER NOT NULL,
            puzzle_day INTEGER NOT NULL,
            puzzle_part INTEGER NOT NULL,
            prompt TEXT,
            program TEXT,
            result TEXT,
            answer TEXT,
            correct BOOLEAN,
            timeout INTEGER,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            error_message TEXT,
            previous_attempt_timed_out BOOLEAN DEFAULT FALSE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quota_limits (
            model_family TEXT PRIMARY KEY,
            last_quota_exceeded TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

def add_experiment(model_family: str, model_name: str, puzzle_year: int, puzzle_day: int, puzzle_part: int, prompt: str, previous_attempt_timed_out: bool) -> int:
    """Adds a new experiment to the database.

    Args:
        model_family: The model family.
        model_name: The model name.
        puzzle_year: The puzzle year.
        puzzle_day: The puzzle day.
        puzzle_part: The puzzle part.
        prompt: The generated prompt.
        previous_attempt_timed_out: Whether or not a previous attempt timed out

    Returns:
        The ID of the newly created experiment.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO experiments (model_family, model_name, puzzle_year, puzzle_day, puzzle_part, prompt, previous_attempt_timed_out)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (model_family, model_name, puzzle_year, puzzle_day, puzzle_part, prompt, previous_attempt_timed_out))

    experiment_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return experiment_id

def update_experiment(experiment_id: int, program: str, result: str, answer: str, correct: bool, timeout: int, error_message: str) -> None:
    """Updates an existing experiment in the database.

    Args:
        experiment_id: The ID of the experiment to update.
        program: The generated program.
        result: The result of running the program (success, timeout, error).
        answer: The output of the program (if successful).
        correct: Whether the answer is correct.
        timeout: The timeout used for running the program
        error_message: Any error messages encountered.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE experiments
        SET program = ?, result = ?, answer = ?, correct = ?, timeout = ?, error_message = ?, end_time = CURRENT_TIMESTAMP
        WHERE experiment_id = ?
    """, (program, result, answer, correct, timeout, error_message, experiment_id))

    conn.commit()
    conn.close()

def get_experiment_by_id(experiment_id: int) -> Tuple:
    """Retrieves an experiment from the database by its ID.

    Args:
        experiment_id: The ID of the experiment to retrieve.

    Returns:
        A tuple representing the experiment, or None if not found.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM experiments WHERE experiment_id = ?", (experiment_id,))
    experiment = cursor.fetchone()

    conn.close()
    return experiment

def get_incomplete_experiments() -> List[Tuple]:
    """Retrieves all experiments that have not been completed yet, excluding those
    where the associated model family's quota has been exceeded within the last hour.

    Returns:
        A list of tuples, where each tuple represents an incomplete experiment.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * 
        FROM experiments
        WHERE result IS NULL
        AND model_family NOT IN (
            SELECT model_family
            FROM quota_limits
            WHERE last_quota_exceeded >= datetime('now', '-1 hour')
        )
    """)
    experiments = cursor.fetchall()

    conn.close()
    return experiments

def get_experiments_by_status(result: str) -> List[Tuple]:
    """Retrieves all experiments with a specific status.

    Args:
        result: The status to filter by (e.g., 'success', 'timeout', 'error').

    Returns:
        A list of tuples, where each tuple represents an experiment with the given status.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM experiments WHERE result = ?", (result,))
    experiments = cursor.fetchall()

    conn.close()
    return experiments

def count_experiments() -> Tuple[int, int]:
    """Counts the number of experiments that have been run and the number of experiments remaining.

    Returns:
        A tuple containing (number_of_experiments_run, number_of_experiments_remaining).
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM experiments")
    total_experiments = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM experiments WHERE result IS NOT NULL")
    completed_experiments = cursor.fetchone()[0]
    
    remaining_experiments = total_experiments - completed_experiments

    conn.close()
    return completed_experiments, remaining_experiments
    
def get_model_family_rankings() -> List[Tuple[str, float]]:
    """Ranks model families by their success rate.

    Returns:
        A list of tuples, where each tuple contains (model_family, success_rate).
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT model_family, AVG(correct) AS success_rate
        FROM experiments
        WHERE result = 'success'
        GROUP BY model_family
        ORDER BY success_rate DESC
    """)
    rankings = cursor.fetchall()

    conn.close()
    return rankings

def get_model_rankings_within_family(model_family: str) -> List[Tuple[str, float]]:
    """Ranks models within a given model family by their success rate.

    Args:
        model_family: The model family to filter by.

    Returns:
        A list of tuples, where each tuple contains (model_name, success_rate).
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT model_name, AVG(correct) AS success_rate
        FROM experiments
        WHERE result = 'success' AND model_family = ?
        GROUP BY model_name
        ORDER BY success_rate DESC
    """, (model_family,))
    rankings = cursor.fetchall()

    conn.close()
    return rankings

def get_year_rankings() -> List[Tuple[int, float]]:
    """Ranks puzzle years by their difficulty (average success rate).

    Returns:
        A list of tuples, where each tuple contains (puzzle_year, average_success_rate).
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT puzzle_year, AVG(correct) AS average_success_rate
        FROM experiments
        WHERE result = 'success'
        GROUP BY puzzle_year
        ORDER BY average_success_rate
    """)
    rankings = cursor.fetchall()

    conn.close()
    return rankings
    
def record_quota_exceeded(model_family: str) -> None:
    """Records that the quota for a model family has been exceeded.

    Args:
        model_family: The model family for which the quota was exceeded.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO quota_limits (model_family, last_quota_exceeded)
        VALUES (?, CURRENT_TIMESTAMP)
    """, (model_family,))

    conn.commit()
    conn.close()

def get_quota_exceeded_families() -> List[str]:
    """Retrieves a list of model families for which the quota has been exceeded within the last hour.

    Returns:
        A list of model family names.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT model_family
        FROM quota_limits
        WHERE last_quota_exceeded >= datetime('now', '-1 hour')
    """)
    families = [row[0] for row in cursor.fetchall()]

    conn.close()
    return families

def get_all_experiments() -> List[Tuple]:
    """Retrieves all experiments from the database.

    Returns:
        A list of tuples, where each tuple represents an experiment.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM experiments")
    all_experiments = cursor.fetchall()
    conn.close()
    return all_experiments
