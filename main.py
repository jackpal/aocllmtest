# main.py
import argparse
import db
import strategy
import webserver
import sys
import csv
import threading
import time

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
            current_status = "Waiting for quota timeout or new experiments"
            print("No more experiments to run at the moment.")
            time.sleep(60) # Wait for a minute before checking again
        else:
            model_family, model_name, year, day, part, timeout, previous_attempt_timed_out = next_experiment
            current_status = f"Running: {model_family} {model_name}, Year: {year}, Day: {day}, Part: {part}, Timeout: {timeout}, Previous Attempt Timed Out: {previous_attempt_timed_out}"
            strategy.run_experiment(*next_experiment)

def main():
    """Parses command-line arguments and runs the appropriate functions."""
    parser = argparse.ArgumentParser(description="Run Advent of Code experiments.")
    parser.add_argument("--csv", metavar="output_file.csv", help="Generate a CSV report of the experiments.")
    parser.add_argument("--webserver", action="store_true", help="Start the webserver.")
    parser.add_argument("--run-experiments", action="store_true", help="Run the experiments.")

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
        webserver.app.run(debug=True)
    
    if not any(vars(args).values()):
        parser.print_help()

if __name__ == "__main__":
    main()