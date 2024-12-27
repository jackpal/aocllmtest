from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import argparse

app = Flask(__name__)
DATABASE = 'puzzles.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get current status
    cursor.execute("""
        SELECT e.model_family, e.model_name, e.year, e.day, e.part, e.status, e.timestamp, q.timeout
        FROM experiments e
        LEFT JOIN quota_timeouts q ON e.model_family = q.model_family
        ORDER BY e.timestamp DESC
        LIMIT 1
    """)
    current_status = cursor.fetchone()

    # Get experiment stats
    cursor.execute("SELECT COUNT(*) FROM experiments")
    total_experiments = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM experiments WHERE status = 'answer' AND correct = TRUE")
    solved_experiments = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM experiments WHERE status = 'timeout'")
    timedout_experiments = cursor.fetchone()[0]

    # Get model family rankings
    cursor.execute("""
        SELECT model_family, AVG(correct) as avg_correct
        FROM experiments
        WHERE status = 'answer'
        GROUP BY model_family
        ORDER BY avg_correct DESC
    """)
    model_family_rankings = cursor.fetchall()
    
    # Get model rankings within each family
    model_rankings = {}
    for family in [row['model_family'] for row in model_family_rankings]:
        cursor.execute("""
            SELECT model_name, AVG(correct) as avg_correct
            FROM experiments
            WHERE status = 'answer' AND model_family = ?
            GROUP BY model_name
            ORDER BY avg_correct DESC
        """, (family,))
        model_rankings[family] = cursor.fetchall()
        
    # Get puzzle year rankings
    cursor.execute("""
        SELECT year, AVG(correct) as avg_correct
        FROM experiments
        WHERE status = 'answer'
        GROUP BY year
        ORDER BY avg_correct ASC
    """)
    year_rankings = cursor.fetchall()

    conn.close()

    return render_template('index.html',
                           current_status=current_status,
                           total_experiments=total_experiments,
                           solved_experiments=solved_experiments,
                           timedout_experiments=timedout_experiments,
                           model_family_rankings=model_family_rankings,
                           model_rankings=model_rankings,
                           year_rankings=year_rankings
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
        cursor.execute("DELETE FROM experiments WHERE id = ?", (experiment_id,))
    elif model_family and model_name and year:
        cursor.execute("DELETE FROM experiments WHERE model_family = ? AND model_name = ? AND year = ?", (model_family, model_name, year))
    elif model_family and year:
        cursor.execute("DELETE FROM experiments WHERE model_family = ? AND year = ?", (model_family, year))
    elif year:
        cursor.execute("DELETE FROM experiments WHERE year = ?", (year,))
    
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

@app.route('/experiments')
def experiments():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM experiments
        ORDER BY timestamp DESC
    """)
    all_experiments = cursor.fetchall()
    
    conn.close()
    
    return render_template('experiments.html', all_experiments=all_experiments)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Web server for viewing experiment results.")
    parser.add_argument("-p", "--port", type=int, default=5000, help="Port to run the web server on.")
    args = parser.parse_args()

    app.run(debug=True, port=args.port)
