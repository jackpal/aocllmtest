import sqlite3
import argparse
import aoc_api

DATABASE = 'puzzles.db'

def initialize_database(conn):
    """Creates the database tables and pre-populates model families and models."""
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS puzzles (
            year INTEGER,
            day INTEGER,
            part INTEGER,
            instructions TEXT,
            solved BOOLEAN DEFAULT FALSE,
            PRIMARY KEY (year, day, part)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS model_families (
            name TEXT PRIMARY KEY
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS models (
            family TEXT,
            name TEXT,
            PRIMARY KEY (family, name),
            FOREIGN KEY (family) REFERENCES model_families(name)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS experiments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_family TEXT,
            model_name TEXT,
            year INTEGER,
            day INTEGER,
            part INTEGER,
            prompt TEXT,
            program TEXT,
            status TEXT CHECK( status IN ('error','timeout','answer','quota') ),
            result TEXT,
            answer TEXT,
            correct BOOLEAN,
            timed_out BOOLEAN DEFAULT FALSE,
            timeout INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(model_family, model_name, year, day, part),
            FOREIGN KEY (model_family) REFERENCES model_families(name)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quota_timeouts (
            model_family TEXT PRIMARY KEY,
            timeout DATETIME,
            FOREIGN KEY (model_family) REFERENCES model_families(name)
        )
    ''')

    # Pre-populate model families and models
    for family in aoc_api.modelfamilies():
        cursor.execute("INSERT OR IGNORE INTO model_families (name) VALUES (?)", (family,))
        for model in aoc_api.models(family):
            cursor.execute("INSERT OR IGNORE INTO models (family, name) VALUES (?, ?)", (family, model))
            
    # Pre-populate puzzles
    for year in range(2015, 2025):
        for day in range(1, 26):
            for part in range(1, 3):
                cursor.execute("INSERT OR IGNORE INTO puzzles (year, day, part) VALUES (?, ?, ?)", (year, day, part))

    conn.commit()
    print("Database initialized.")

def display_status(conn):
    """Displays the current status of the database."""
    cursor = conn.cursor()

    # Get last experiment
    cursor.execute("""
        SELECT e.model_family, e.model_name, e.year, e.day, e.part, e.status, e.timestamp, q.timeout
        FROM experiments e
        LEFT JOIN quota_timeouts q ON e.model_family = q.model_family
        ORDER BY e.timestamp DESC
        LIMIT 1
    """)
    last_experiment = cursor.fetchone()

    if last_experiment:
        print("Last Experiment:")
        print(f"  Model Family: {last_experiment[0]}")
        print(f"  Model Name: {last_experiment[1]}")
        print(f"  Puzzle: {last_experiment[2]}/{last_experiment[3]}/{last_experiment[4]}")
        print(f"  Status: {last_experiment[5]}")
        print(f"  Timestamp: {last_experiment[6]}")
        if last_experiment[7]:
            print(f"  Quota Timeout: {last_experiment[7]}")
    else:
        print("No experiments run yet.")

    # Get experiment counts
    cursor.execute("SELECT COUNT(*) FROM experiments")
    total_experiments = cursor.fetchone()[0]
    print(f"\nTotal Experiments: {total_experiments}")

    cursor.execute("SELECT COUNT(*) FROM experiments WHERE status = 'answer' AND correct = TRUE")
    solved_experiments = cursor.fetchone()[0]
    print(f"Solved Experiments: {solved_experiments}")

    cursor.execute("SELECT COUNT(*) FROM experiments WHERE status = 'timeout'")
    timedout_experiments = cursor.fetchone()[0]
    print(f"Timed-out Experiments: {timedout_experiments}")
    
    # Get unsolved puzzles
    cursor.execute("SELECT COUNT(*) FROM puzzles WHERE solved = FALSE")
    unsolved_puzzles = cursor.fetchone()[0]
    print(f"Unsolved Puzzles: {unsolved_puzzles}")

def delete_experiments(conn, experiment_id, model_family, model_name, year):
    """Deletes experiment records based on the provided criteria."""
    cursor = conn.cursor()

    if experiment_id:
        cursor.execute("DELETE FROM experiments WHERE id = ?", (experiment_id,))
    elif model_family and model_name and year:
        cursor.execute("DELETE FROM experiments WHERE model_family = ? AND model_name = ? AND year = ?", (model_family, model_name, year))
    elif model_family and year:
        cursor.execute("DELETE FROM experiments WHERE model_family = ? AND year = ?", (model_family, year))
    elif year:
        cursor.execute("DELETE FROM experiments WHERE year = ?", (year,))
    else:
        print("No valid criteria provided for deletion.")
        return

    conn.commit()
    print(f"Deleted {cursor.rowcount} experiments.")

def main():
    parser = argparse.ArgumentParser(description="Database manager for Advent of Code experiment runner.")
    parser.add_argument("-i", "--init", action="store_true", help="Initialize the database.")
    parser.add_argument("-s", "--status", action="store_true", help="Display database status.")
    parser.add_argument("-d", "--delete", action="store_true", help="Delete experiment records.")
    parser.add_argument("-id", "--experiment_id", type=int, help="Experiment ID to delete.")
    parser.add_argument("-mf", "--model_family", type=str, help="Model family to filter by (for deletion).")
    parser.add_argument("-mn", "--model_name", type=str, help="Model name to filter by (for deletion).")
    parser.add_argument("-y", "--year", type=int, help="Year to filter by (for deletion).")
    args = parser.parse_args()

    conn = sqlite3.connect(DATABASE)

    if args.init:
        initialize_database(conn)

    if args.status:
        display_status(conn)

    if args.delete:
        delete_experiments(conn, args.experiment_id, args.model_family, args.model_name, args.year)

    conn.close()

if __name__ == "__main__":
    main()
