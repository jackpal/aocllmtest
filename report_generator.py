import sqlite3
import argparse
import csv
from db_util import create_or_open_puzzle_db

def generate_current_status_report(cursor):
    """Generates a report on the current status of the experiment runner."""

    cursor.execute("""
        SELECT e.*, q.timeout_until
        FROM Experiments e
        LEFT JOIN QuotaTimeouts q ON e.model_family = q.model_family
        WHERE e.experiment_started_at = (SELECT MAX(experiment_started_at) FROM Experiments)
    """)
    current_experiment = cursor.fetchone()

    cursor.execute("SELECT model_family, timeout_until FROM QuotaTimeouts WHERE timeout_until > ?", (datetime.datetime.now(),))
    quota_status = cursor.fetchall()

    print("## Current Status Report\n")

    if current_experiment:
        print(f"**Currently running experiment:**\n")
        print(f"- Experiment ID: {current_experiment[0]}")
        print(f"- Model Family: {current_experiment[1]}")
        print(f"- Model Name: {current_experiment[2]}")
        print(f"- Puzzle: {current_experiment[3]}/{current_experiment[4]}/{current_experiment[5]}")
        print(f"- Status: {current_experiment[7]}")
        if current_experiment[8]:
            print(f"- Error Message: {current_experiment[8]}")
        if current_experiment[9]:
            print(f"- Timeout (seconds): {current_experiment[9]}")
        if current_experiment[10]:
            print(f"- Answer: {current_experiment[10]}")
        print(f"- Answer is Correct: {current_experiment[11]}")
        print(f"- Started at: {current_experiment[12]}")
        if current_experiment[13]:
            print(f"- Finished at: {current_experiment[13]}")
    else:
        print("**No experiment is currently running.**\n")

    if quota_status:
        print("\n**Quota Timeouts:**\n")
        for model_family, timeout_until in quota_status:
            print(f"- {model_family}: until {timeout_until}")
    else:
        print("\n**No active quota timeouts.**\n")

def generate_experiment_counts_report(cursor):
    """Generates a report on the number of experiments run and remaining."""

    cursor.execute("SELECT COUNT(*) FROM Experiments")
    total_experiments = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Experiments WHERE answer_is_correct = 1")
    solved_experiments = cursor.fetchone()[0]

    total_possible_experiments = len(model_families()) * sum(len(models(mf)) for mf in model_families()) * (2024-2015) * 25 * 2
    remaining_experiments = total_possible_experiments - total_experiments
    
    print("## Experiment Counts Report\n")
    print(f"- Total Experiments Run: {total_experiments}")
    print(f"- Solved Experiments: {solved_experiments}")
    print(f"- Remaining Experiments: {remaining_experiments}")
    print(f"- Total Possible Experiments: {total_possible_experiments}")

def generate_model_family_ranking_report(cursor):
    """Generates a report ranking model families by puzzle solving success."""
    cursor.execute("SELECT * FROM ModelFamilyRank ORDER BY success_rate DESC")
    model_family_ranks = cursor.fetchall()

    print("## Model Family Rankings\n")
    print("| Rank | Model Family | Solved | Attempted | Success Rate |")
    print("|---|---|---|---|---|")
    for i, row in enumerate(model_family_ranks):
        print(f"| {i+1} | {row[0]} | {row[1]} | {row[2]} | {row[3]:.2f} |")

def generate_model_ranking_report(cursor):
    """Generates a report ranking models within each family by puzzle solving success."""
    cursor.execute("SELECT * FROM ModelRank ORDER BY model_family, success_rate DESC")
    model_ranks = cursor.fetchall()

    print("## Model Rankings\n")
    current_family = None
    for row in model_ranks:
        if row[0] != current_family:
            current_family = row[0]
            print(f"\n### {current_family}\n")
            print("| Rank | Model | Solved | Attempted | Success Rate |")
            print("|---|---|---|---|---|")
        print(f"|  | {row[1]} | {row[2]} | {row[3]} | {row[4]:.2f} |")

def generate_year_ranking_report(cursor):
    """Generates a report ranking puzzle years by difficulty."""
    cursor.execute("SELECT * FROM YearRank ORDER BY success_rate ASC")
    year_ranks = cursor.fetchall()

    print("## Year Rankings (by Difficulty)\n")
    print("| Rank | Year | Solved | Attempted | Success Rate |")
    print("|---|---|---|---|---|")
    for i, row in enumerate(year_ranks):
        print(f"| {i+1} | {row[0]} | {row[1]} | {row[2]} | {row[3]:.2f} |")

def generate_csv_reports(cursor, args):
    """Generates CSV reports based on command line arguments."""

    if args.csv_all or args.csv_model_family_ranking:
        cursor.execute("SELECT * FROM ModelFamilyRank ORDER BY success_rate DESC")
        with open("model_family_ranking.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Model Family", "Solved", "Attempted", "Success Rate"])
            writer.writerows(cursor.fetchall())
        print("Generated model_family_ranking.csv")

    if args.csv_all or args.csv_model_ranking:
        cursor.execute("SELECT * FROM ModelRank ORDER BY model_family, success_rate DESC")
        with open("model_ranking.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Model Family", "Model", "Solved", "Attempted", "Success Rate"])
            writer.writerows(cursor.fetchall())
        print("Generated model_ranking.csv")

def generate_csv_reports(cursor, args):
    """Generates CSV reports based on command line arguments."""

    if args.csv_all or args.csv_model_family_ranking:
        cursor.execute("SELECT * FROM ModelFamilyRank ORDER BY success_rate DESC")
        with open("model_family_ranking.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Model Family", "Solved", "Attempted", "Success Rate"])
            writer.writerows(cursor.fetchall())
        print("Generated model_family_ranking.csv")

    if args.csv_all or args.csv_model_ranking:
        cursor.execute("SELECT * FROM ModelRank ORDER BY model_family, success_rate DESC")
        with open("model_ranking.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Model Family", "Model", "Solved", "Attempted", "Success Rate"])
            writer.writerows(cursor.fetchall())
        print("Generated model_ranking.csv")

    if args.csv_all or args.csv_year_ranking:
        cursor.execute("SELECT * FROM YearRank ORDER BY success_rate ASC")
        with open("year_ranking.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Year", "Solved", "Attempted", "Success Rate"])
            writer.writerows(cursor.fetchall())
        print("Generated year_ranking.csv")

    if args.csv_all or args.csv_experiments:
        cursor.execute("SELECT * FROM Experiments")
        with open("experiments.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([description[0] for description in cursor.description])  # Write header row
            writer.writerows(cursor.fetchall())
        print("Generated experiments.csv")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Report generator for the experiment database.")
    parser.add_argument("--current_status", action="store_true", help="Generate the current status report")
    parser.add_argument("--experiment_counts", action="store_true", help="Generate the experiment counts report")
    parser.add_argument("--model_family_ranking", action="store_true", help="Generate the model family ranking report")
    parser.add_argument("--model_ranking", action="store_true", help="Generate the model ranking report")
    parser.add_argument("--year_ranking", action="store_true", help="Generate the year ranking report")
    parser.add_argument("--all", action="store_true", help="Generate all markdown reports")

    parser.add_argument("--csv_model_family_ranking", action="store_true", help="Generate the model family ranking CSV")
    parser.add_argument("--csv_model_ranking", action="store_true", help="Generate the model ranking CSV")
    parser.add_argument("--csv_year_ranking", action="store_true", help="Generate the year ranking CSV")
    parser.add_argument("--csv_experiments", action="store_true", help="Generate the experiments CSV")
    parser.add_argument("--csv_all", action="store_true", help="Generate all CSV reports")

    args = parser.parse_args()

    conn = create_or_open_puzzle_db()
    cursor = conn.cursor()

    if args.all or args.current_status:
        generate_current_status_report(cursor)
    if args.all or args.experiment_counts:
        generate_experiment_counts_report(cursor)
    if args.all or args.model_family_ranking:
        generate_model_family_ranking_report(cursor)
    if args.all or args.model_ranking:
        generate_model_ranking_report(cursor)
    if args.all or args.year_ranking:
        generate_year_ranking_report(cursor)

    generate_csv_reports(cursor, args)

    conn.close()
