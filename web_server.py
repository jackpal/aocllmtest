from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from db_util import create_or_open_puzzle_db
import argparse

app = Flask(__name__)

def get_db_connection():
    conn = create_or_open_puzzle_db()
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get current experiment status
    cursor.execute("""
        SELECT e.*, q.timeout_until
        FROM Experiments e
        LEFT JOIN QuotaTimeouts q ON e.model_family = q.model_family
        WHERE e.experiment_started_at = (SELECT MAX(experiment_started_at) FROM Experiments)
    """)
    current_experiment = cursor.fetchone()

    # Check if currently waiting due to quota exhaustion
    cursor.execute("SELECT model_family, timeout_until FROM QuotaTimeouts WHERE timeout_until > ?", (datetime.datetime.now(),))
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

    conn.close()

    return render_template(
        'index.html',
        current_experiment=current_experiment,
        quota_status=quota_status,
        total_experiments=total_experiments,
        solved_experiments=solved_experiments,
        model_family_ranks=model_family_ranks,
        model_ranks=model_ranks,
        year_ranks=year_ranks
    )

@app.route('/delete', methods=['POST'])
def delete_experiments():
    conn = get_db_connection()
    cursor = conn.cursor()

    experiment_id = request.form.get('experiment_id')
    model_family = request.form.get('model_family')
    model_name = request.form.get('model_name')
    year = request.form.get('year')

    if experiment_id:
        cursor.execute("DELETE FROM Experiments WHERE experiment_id = ?", (experiment_id,))
    elif model_family and model_name and year:
        cursor.execute("DELETE FROM Experiments WHERE model_family = ? AND model_name = ? AND puzzle_year = ?", (model_family, model_name, year))
    elif model_family and year:
        cursor.execute("DELETE FROM Experiments WHERE model_family = ? AND puzzle_year = ?", (model_family, year))
    elif year:
        cursor.execute("DELETE FROM Experiments WHERE puzzle_year = ?", (year,))

    conn.commit()
    conn.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Web server for viewing experiment results.")
    parser.add_argument("--port", type=int, default=5000, help="Port to run the web server on")
    args = parser.parse_args()

    app.run(debug=True, port=args.port)
