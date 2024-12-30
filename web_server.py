from flask import Flask, render_template
import sqlite3
from db_util import create_or_open_puzzle_db
import argparse
import datetime

app = Flask(__name__)

def get_db_connection():
    conn = create_or_open_puzzle_db()
    conn.row_factory = sqlite3.Row
    return conn

def calculate_summary_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get all model families and models
    cursor.execute("SELECT model_family FROM ModelFamilies")
    model_families = [row['model_family'] for row in cursor.fetchall()]

    cursor.execute("SELECT model_name FROM Models")
    models = [row['model_name'] for row in cursor.fetchall()]

    # Get all years
    cursor.execute("SELECT DISTINCT puzzle_year FROM Experiments ORDER BY puzzle_year")
    years = [row['puzzle_year'] for row in cursor.fetchall()]

    summary_data = {}
    totals = {}

    for year in years + ["All"]:
        summary_data[year] = {}
        totals[year] = {"Part 1": {}, "Part 2": {}}

        for model_family in model_families:
            summary_data[year][model_family] = {}

            # Get models for this model_family
            cursor.execute("SELECT model_name FROM Models WHERE model_family = ?", (model_family,))
            models_in_family = [row['model_name'] for row in cursor.fetchall()]

            for model in models_in_family:
                summary_data[year][model_family][model] = {}

                for part in [1, 2]:
                    if year == "All":
                        cursor.execute("""
                            SELECT
                                COUNT(CASE WHEN answer_is_correct = 1 THEN 1 END) as correct,
                                COUNT(CASE WHEN answer_is_correct = 0 THEN 1 END) as incorrect,
                                COUNT(CASE WHEN run_status = 'timeout' THEN 1 END) as timed_out,
                                COUNT(CASE WHEN run_status = 'error' THEN 1 END) as error,
                                COUNT(CASE WHEN run_status IS NULL THEN 1 END) as not_attempted,
                                COUNT(*) as total
                            FROM Experiments
                            WHERE model_family = ? AND model_name = ? AND puzzle_part = ?
                        """, (model_family, model, part))
                    else:
                        cursor.execute("""
                            SELECT
                                COUNT(CASE WHEN answer_is_correct = 1 THEN 1 END) as correct,
                                COUNT(CASE WHEN answer_is_correct = 0 THEN 1 END) as incorrect,
                                COUNT(CASE WHEN run_status = 'timeout' THEN 1 END) as timed_out,
                                COUNT(CASE WHEN run_status = 'error' THEN 1 END) as error,
                                COUNT(CASE WHEN run_status IS NULL THEN 1 END) as not_attempted,
                                COUNT(*) as total
                            FROM Experiments
                            WHERE model_family = ? AND model_name = ? AND puzzle_year = ? AND puzzle_part = ?
                        """, (model_family, model, year, part))

                    result = cursor.fetchone()
                    summary_data[year][model_family][model][f"Part {part}"] = {
                        "correct": result['correct'],
                        "incorrect": result['incorrect'],
                        "timed_out": result['timed_out'],
                        "error": result['error'],
                        "not_attempted": result['not_attempted'],
                        "total": result['total'],
                        "correct_pct": 0 if result['total'] == 0 else (result['correct'] / result['total']) * 100,
                        "incorrect_pct": 0 if result['total'] == 0 else (result['incorrect'] / result['total']) * 100,
                        "timed_out_pct": 0 if result['total'] == 0 else (result['timed_out'] / result['total']) * 100,
                        "error_pct": 0 if result['total'] == 0 else (result['error'] / result['total']) * 100,
                        "not_attempted_pct": 0 if result['total'] == 0 else (result['not_attempted'] / result['total']) * 100,
                    }

                    # Accumulate totals for each part
                    for key in ["correct", "incorrect", "timed_out", "error", "not_attempted", "total"]:
                        totals[year][f"Part {part}"][key] = totals[year][f"Part {part}"].get(key, 0) + summary_data[year][model_family][model][f"Part {part}"][key]

        # Calculate percentages for totals
        for part in [1, 2]:
            total_part = totals[year][f"Part {part}"]["total"]
            totals[year][f"Part {part}"]["correct_pct"] = 0 if total_part == 0 else (totals[year][f"Part {part}"]["correct"] / total_part) * 100
            totals[year][f"Part {part}"]["incorrect_pct"] = 0 if total_part == 0 else (totals[year][f"Part {part}"]["incorrect"] / total_part) * 100
            totals[year][f"Part {part}"]["timed_out_pct"] = 0 if total_part == 0 else (totals[year][f"Part {part}"]["timed_out"] / total_part) * 100
            totals[year][f"Part {part}"]["error_pct"] = 0 if total_part == 0 else (totals[year][f"Part {part}"]["error"] / total_part) * 100
            totals[year][f"Part {part}"]["not_attempted_pct"] = 0 if total_part == 0 else (totals[year][f"Part {part}"]["not_attempted"] / total_part) * 100

    conn.close()
    return summary_data, totals, model_families, models

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get current experiment status
    cursor.execute("""
        SELECT e.*, q.timeout_until
        FROM Experiments e
        LEFT JOIN QuotaTimeouts q ON e.model_name = q.model_name
        WHERE e.experiment_started_at = (SELECT MAX(experiment_started_at) FROM Experiments)
    """)
    current_experiment = cursor.fetchone()

    # Check if currently waiting due to quota exhaustion
    cursor.execute("SELECT model_name, timeout_until FROM QuotaTimeouts WHERE timeout_until > ?", (datetime.datetime.now(),))
    quota_status = cursor.fetchall()

    # Get counts of experiments
    cursor.execute("SELECT COUNT(*) FROM Experiments")
    total_experiments = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Experiments WHERE answer_is_correct = 1")
    solved_experiments = cursor.fetchone()[0]

    # Model Family Rankings
    cursor.execute("SELECT * FROM ModelFamilyRank ORDER BY success_rate DESC")
    model_family_ranks = cursor.fetchall()

    # Model Rankings
    cursor.execute("SELECT * FROM ModelRank ORDER BY success_rate DESC")
    model_ranks = cursor.fetchall()

    # Year Rankings
    cursor.execute("SELECT * FROM YearRank ORDER BY success_rate DESC")
    year_ranks = cursor.fetchall()

    summary_data, totals, model_families, models = calculate_summary_data()

    conn.close()

    return render_template(
        'index.html',
        current_experiment=current_experiment,
        quota_status=quota_status,
        total_experiments=total_experiments,
        solved_experiments=solved_experiments,
        model_family_ranks=model_family_ranks,
        model_ranks=model_ranks,
        year_ranks=year_ranks,
        summary_data=summary_data,
        totals=totals,
        model_families=model_families,
        models=models
    )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Web server for viewing experiment results.")
    parser.add_argument("--port", type=int, default=5000, help="Port to run the web server on")
    args = parser.parse_args()

    app.run(debug=True, port=args.port)
