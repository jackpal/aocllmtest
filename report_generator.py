import sqlite3
import argparse
import csv

DATABASE = 'puzzles.db'

def generate_markdown_report(conn):
    """Generates a Markdown report of the experiment results."""
    cursor = conn.cursor()

    # Header
    report = "# Advent of Code Experiment Results\n\n"

    # Current Status
    cursor.execute("""
        SELECT e.model_family, e.model_name, e.year, e.day, e.part, e.status, e.timestamp, q.timeout
        FROM experiments e
        LEFT JOIN quota_timeouts q ON e.model_family = q.model_family
        ORDER BY e.timestamp DESC
        LIMIT 1
    """)
    current_status = cursor.fetchone()

    report += "## Current Status\n\n"
    if current_status:
        report += f"- **Last Experiment:**\n"
        report += f"    - Model Family: {current_status[0]}\n"
        report += f"    - Model Name: {current_status[1]}\n"
        report += f"    - Puzzle: {current_status[2]}/{current_status[3]}/{current_status[4]}\n"
        report += f"    - Status: {current_status[5]}\n"
        report += f"    - Timestamp: {current_status[6]}\n"
        if current_status[7]:
            report += f"    - Quota Timeout: {current_status[7]}\n"
    else:
        report += "No experiments run yet.\n"

    # Experiment Summary
    cursor.execute("SELECT COUNT(*) FROM experiments")
    total_experiments = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM experiments WHERE status = 'answer' AND correct = TRUE")
    solved_experiments = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM experiments WHERE status = 'timeout'")
    timedout_experiments = cursor.fetchone()[0]

    report += "\n## Experiment Summary\n\n"
    report += f"- **Total Experiments:** {total_experiments}\n"
    report += f"- **Solved Experiments:** {solved_experiments}\n"
    report += f"- **Timed-out Experiments:** {timedout_experiments}\n"
    
    # Get unsolved puzzles
    cursor.execute("SELECT COUNT(*) FROM puzzles WHERE solved = FALSE")
    unsolved_puzzles = cursor.fetchone()[0]
    report += f"- **Unsolved Puzzles:** {unsolved_puzzles}\n"

    # Model Family Rankings
    cursor.execute("""
        SELECT model_family, AVG(correct) as avg_correct
        FROM experiments
        WHERE status = 'answer'
        GROUP BY model_family
        ORDER BY avg_correct DESC
    """)
    model_family_rankings = cursor.fetchall()

    report += "\n## Model Family Rankings\n\n"
    report += "| Model Family | Average Correctness |\n"
    report += "|---|---| \n"
    for row in model_family_rankings:
        report += f"| {row[0]} | {row[1]:.2f} |\n"
    
    # Model rankings within each family
    report += "\n## Model Rankings (by Family)\n\n"
    for family in [row[0] for row in model_family_rankings]:
        cursor.execute("""
            SELECT model_name, AVG(correct) as avg_correct
            FROM experiments
            WHERE status = 'answer' AND model_family = ?
            GROUP BY model_name
            ORDER BY avg_correct DESC
        """, (family,))
        model_rankings = cursor.fetchall()

        report += f"### {family}\n\n"
        report += "| Model Name | Average Correctness |\n"
        report += "|---|---| \n"
        for row in model_rankings:
            report += f"| {row[0]} | {row[1]:.2f} |\n"

    # Puzzle Year Rankings
    cursor.execute("""
        SELECT year, AVG(correct) as avg_correct
        FROM experiments
        WHERE status = 'answer'
        GROUP BY year
        ORDER BY avg_correct ASC
    """)
    year_rankings = cursor.fetchall()

    report += "\n## Puzzle Year Rankings (Easiest to Hardest)\n\n"
    report += "| Year | Average Correctness |\n"
    report += "|---|---| \n"
    for row in year_rankings:
        report += f"| {row[0]} | {row[1]:.2f} |\n"

    print(report)

def generate_csv_report(conn):
    """Generates a CSV report of the experiment results."""
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM experiments")
    experiments = cursor.fetchall()

    print("experiment_id,model_family,model_name,year,day,part,status,result,answer,correct,timed_out,timeout,timestamp")
    writer = csv.writer(sys.stdout)
    for row in experiments:
        writer.writerow(row)

def main():
    parser = argparse.ArgumentParser(description="Report generator for Advent of Code experiment results.")
    parser.add_argument("-m", "--markdown", action="store_true", help="Generate Markdown report.")
    parser.add_argument("-c", "--csv", action="store_true", help="Generate CSV report.")
    args = parser.parse_args()

    conn = sqlite3.connect(DATABASE)

    if args.markdown:
        generate_markdown_report(conn)

    if args.csv:
        generate_csv_report(conn)

    conn.close()

if __name__ == "__main__":
    main()
