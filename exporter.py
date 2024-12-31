import sqlite3
import csv
from db_util import create_or_open_puzzle_db

def export_results_to_csv(db_name="puzzle.db", csv_file="results.csv"):
    """
    Exports experiment results from the SQLite database to a CSV file.

    Args:
        db_name: The name of the SQLite database file.
        csv_file: The name of the CSV file to export to.
    """

    conn = create_or_open_puzzle_db(db_name)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            model_family,
            model_name,
            puzzle_year,
            puzzle_day,
            puzzle_part,
            run_status,
            answer_is_correct
        FROM Experiments
        ORDER BY puzzle_year, puzzle_day, puzzle_part, model_family, model_name
    """)
    results = cursor.fetchall()

    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['model_family', 'model_name', 'puzzle_year', 'puzzle_day', 'puzzle_part', 'status'])  # Header row

        for row in results:
            model_family, model_name, puzzle_year, puzzle_day, puzzle_part, run_status, answer_is_correct = row

            if run_status == 'error':
                status = 'error'
            elif run_status == 'timeout':
                status = 'timeout'
            elif run_status == 'answer':
                status = 'correct' if answer_is_correct else 'incorrect'
            else:
                status = 'unknown'  # Should not normally happen

            writer.writerow([model_family, model_name, puzzle_year, puzzle_day, puzzle_part, status])

    conn.close()
    print(f"Successfully exported results to {csv_file}")

if __name__ == "__main__":
    export_results_to_csv()
