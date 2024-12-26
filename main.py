# main.py
import argparse
import db
import strategy
import webserver
import sys
import csv

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

def main():
    """Parses command-line arguments and runs the appropriate functions."""
    parser = argparse.ArgumentParser(description="Run Advent of Code experiments.")
    parser.add_argument("--csv", metavar="output_file.csv", help="Generate a CSV report of the experiments.")
    parser.add_argument("--webserver", action="store_true", help="Start the webserver.")
    parser.add_argument("--run-experiments", action="store_true", help="Run the experiments.")

    args = parser.parse_args()

    if args.csv:
        generate_csv_report(args.csv)
    
    if args.webserver:
        print("Starting webserver...")
        webserver.app.run(debug=True)

    if args.run_experiments:
        print("Running experiments...")
        strategy.run_all_experiments()

    if not any(vars(args).values()):
        parser.print_help()
        
if __name__ == "__main__":
    main()
    