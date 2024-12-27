# main.py
import argparse
import db
import strategy
import webserver
import sys
import csv
import threading
import time
import datetime

# Global variable to share the current status between run_all_experiments and the webserver
current_status = "Idle"

def generate_csv_report(output_file: str) -> None:
    """Generates a CSV report of all experiments."""
    experiments = db.get_all_experiments()

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "Experiment ID", "Model Family", "Model Name", "Year", "Day", "Part",
            "Prompt", "Program", "Result", "Answer", "Correct", "Timeout", "Start Time", "End Time", "Error Message", "Previous Attempt Timed Out"
        ])

        for exp in experiments:
            writer.writerow(exp)

    print(f"CSV report generated: {output_file}")

def run_experiments_thread():
    """Runs experiments in a separate thread, updating the global current_status."""
    global current_status
    
    db.create_tables()

    while True:
        next_experiment = strategy.get_next_experiment()
        if next_experiment is None:
            # If get_next_experiment returned None, it means there's nothing to do right now.
            # Check if this is due to quota limits.
            earliest_check_time = db.get_earliest_quota_reset_time()
            if earliest_check_time:
                time_to_wait = earliest_check_time - datetime.datetime.now(datetime.timezone.utc)
                wait_seconds = max(0, time_to_wait.total_seconds())
                
                print(f"All model families have exceeded their quota. Waiting until {earliest_check_time.strftime('%Y-%m-%d %H:%M:%S')}...")
                
                # Update the status message to indicate the wait time
                current_status = f"Waiting until {earliest_check_time.strftime('%Y-%m-%d %H:%M:%S')} for quota to reset"

                time.sleep(wait_seconds)
            else:
                # No quota limit found, but still nothing to do. Wait for a shorter period.
                print("No experiments to run at the moment. Waiting for 60 seconds...")
                current_status = "No experiments to run at the moment. Waiting for 60 seconds..."
                time.sleep(60)
        else:
            model_family, model_name, year, day, part, timeout, previous_attempt_timed_out = next_experiment
            current_status = f"Running: {model_family} {model_name}, Year: {year}, Day: {day}, Part: {part}, Timeout: {timeout}, Previous Attempt Timed Out: {previous_attempt_timed_out}"
            strategy.run_experiment(*next_experiment)

def delete_experiments(model_family: str, model_name: str, year: int, day: int, part: int, result: str) -> None:
    """Deletes experiments from the database that match the given filter criteria."""
    conn = db.sqlite3.connect(db.DATABASE_NAME)
    cursor = conn.cursor()

    query = "DELETE FROM experiments WHERE 1=1"
    params = []

    if model_family:
        query += " AND model_family = ?"
        params.append(model_family)
    if model_name:
        query += " AND model_name = ?"
        params.append(model_name)
    if year:
        query += " AND puzzle_year = ?"
        params.append(year)
    if day:
        query += " AND puzzle_day = ?"
        params.append(day)
    if part:
        query += " AND puzzle_part = ?"
        params.append(part)
    if result:
        query += " AND result = ?"
        params.append(result)

    cursor.execute(query, params)
    conn.commit()
    conn.close()

    print(f"Deleted {cursor.rowcount} experiments.")
    
def main():
    """Parses command-line arguments and runs the appropriate functions."""
    parser = argparse.ArgumentParser(description="Run Advent of Code experiments.")
    parser.add_argument("--csv", metavar="output_file.csv", help="Generate a CSV report of the experiments.")
    parser.add_argument("--webserver", action="store_true", help="Start the webserver.")
    parser.add_argument("--run-experiments", action="store_true", help="Run the experiments.")
    parser.add_argument("--delete-experiments", action="store_true", help="Delete experiments based on filter criteria.")
    parser.add_argument("--model-family", help="Filter by model family for deletion.")
    parser.add_argument("--model-name", help="Filter by model name for deletion.")
    parser.add_argument("--year", type=int, help="Filter by year for deletion.")
    parser.add_argument("--day", type=int, help="Filter by day for deletion.")
    parser.add_ar# main.py
import argparse
import db
import strategy
import webserver
import sys
import csv
import threading
import time
import datetime

# ... (other functions remain the same)

def main():
    """Parses command-line arguments and runs the appropriate functions."""
    parser = argparse.ArgumentParser(description="Run Advent of Code experiments.")
    parser.add_argument("--csv", metavar="output_file.csv", help="Generate a CSV report of the experiments.")
    parser.add_argument("--webserver", action="store_true", help="Start the webserver.")
    parser.add_argument("--port", type=int, default=5000, help="Port number for the webserver (default: 5000).")
    parser.add_argument("--run-experiments", action="store_true", help="Run the experiments.")
    parser.add_argument("--delete-experiments", action="store_true", help="Delete experiments based on filter criteria.")
    parser.add_argument("--model-family", help="Filter by model family for deletion.")
    parser.add_argument("--model-name", help="Filter by model name for deletion.")
    parser.add_argument("--year", type=int, help="Filter by year for deletion.")
    parser.add_argument("--day", type=int, help="Filter by day for deletion.")
    parser.add_argument("--part", type=int, help="Filter by part for deletion.")
    parser.add_argument("--result", help="Filter by result for deletion.")

    args = parser.parse_args()

    # Create the database and tables if they don't exist
    db.create_tables()

    if args.csv:
        generate_csv_report(args.csv)

    if args.run_experiments:
        experiment_thread = threading.Thread(target=run_experiments_thread, daemon=True)
        experiment_thread.start()

    if args.webserver:
        print(f"Starting webserver on port {args.port}...")
        # Update webserver to use the global current_status
        webserver.current_status = lambda: current_status
        webserver.app.run(debug=True, port=args.port)

    if args.delete_experiments:
        delete_experiments(args.model_family, args.model_name, args.year, args.day, args.part, args.result)

    if not any(vars(args).values()):
        parser.print_help()

if __name__ == "__main__":
    main()gument("--part", type=int, help="Filter by part for deletion.")
    parser.add_argument("--result", help="Filter by result for deletion.")

    args = parser.parse_args()

    # Create the database and tables if they don't exist
    db.create_tables()

    if args.csv:
        generate_csv_report(args.csv)
    
    if args.run_experiments:
        experiment_thread = threading.Thread(target=run_experiments_thread, daemon=True)
        experiment_thread.start()

    if args.webserver:
        print("Starting webserver...")
        # Update webserver to use the global current_status
        webserver.current_status = lambda: current_status
        webserver.app.run(debug=True, port=8000)

    if args.delete_experiments:
        delete_experiments(args.model_family, args.model_name, args.year, args.day, args.part, args.result)

    if not any(vars(args).values()):
        parser.print_help()

if __name__ == "__main__":
    main()