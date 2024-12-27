import sqlite3
import argparse
import os
from db_util import create_or_open_puzzle_db

def display_db_status(conn):
    """Displays the current status of the database."""
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM Experiments")
    total_experiments = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Experiments WHERE answer_is_correct = 1")
    solved_experiments = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM Experiments ORDER BY experiment_id DESC LIMIT 10")
    recent_experiments = cursor.fetchall()

    print("Database Status:")
    print(f"  Total Experiments: {total_experiments}")
    print(f"  Solved Experiments: {solved_experiments}")
    print("\nRecent Experiments (Last 10):")
    for row in recent_experiments:
        print(f"    ID: {row[0]}, Model: {row[1]}/{row[2]}, Puzzle: {row[3]}/{row[4]}/{row[5]}, Status: {row[7]}, Correct: {row[10]}")

def delete_experiments(conn, args):
    """Deletes experiment records based on command line arguments."""
    cursor = conn.cursor()

    if args.experiment_id:
        cursor.execute("DELETE FROM Experiments WHERE experiment_id = ?", (args.experiment_id,))
        print(f"Deleted experiment with ID: {args.experiment_id}")
    elif args.model_family and args.model_name and args.year:
        cursor.execute("DELETE FROM Experiments WHERE model_family = ? AND model_name = ? AND puzzle_year = ?",
                       (args.model_family, args.model_name, args.year))
        print(f"Deleted experiments for model {args.model_family}/{args.model_name} in year {args.year}")
    elif args.model_family and args.year:
        cursor.execute("DELETE FROM Experiments WHERE model_family = ? AND puzzle_year = ?",
                       (args.model_family, args.year))
        print(f"Deleted experiments for model family {args.model_family} in year {args.year}")
    elif args.year:
        cursor.execute("DELETE FROM Experiments WHERE puzzle_year = ?", (args.year,))
        print(f"Deleted experiments for year {args.year}")
    else:
        print("No deletion criteria specified.")

    conn.commit()

def init_db(db_name="puzzle.db"):
    """Deletes the existing database if it exists, and creates and initializes a new one."""
    if os.path.exists(db_name):
        os.remove(db_name)
        print(f"Deleted existing database: {db_name}")

    conn = create_or_open_puzzle_db(db_name)
    print(f"Created and initialized new database: {db_name}")
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Database manager for the experiment database.")
    parser.add_argument("--status", action="store_true", help="Display the current database status")
    parser.add_argument("--delete", action="store_true", help="Delete experiment records")
    parser.add_argument("--init", action="store_true", help="Initialize the database (deletes existing database if it exists)")
    parser.add_argument("--experiment_id", type=int, help="Experiment ID to delete")
    parser.add_argument("--model_family", type=str, help="Model family to delete experiments for")
    parser.add_argument("--model_name", type=str, help="Model name to delete experiments for")
    parser.add_argument("--year", type=int, help="Year to delete experiments for")

    args = parser.parse_args()

    if args.init:
        init_db()
    else:
        conn = create_or_open_puzzle_db()

        if args.status:
            display_db_status(conn)

        if args.delete:
            delete_experiments(conn, args)

        conn.close()
