# webserver.py
from flask import Flask, render_template, jsonify
import db
import datetime

app = Flask(__name__)

# Function to get the current status (will be set from main.py)
current_status = lambda: "Status not available"

@app.route("/")
def index():
    """Renders the main page of the web application."""
    return render_template("index.html")

@app.route("/status")
def status():
    """Provides data for the status of the experiments."""
    completed_count, remaining_count = db.count_experiments()

    earliest_check_time = db.get_earliest_quota_reset_time()
    if earliest_check_time:
        time_until_reset = earliest_check_time - datetime.datetime.now().astimezone(earliest_check_time.tzinfo)
        time_until_reset_str = str(time_until_reset).split(".")[0]  # Format as HH:MM:SS
    else:
        time_until_reset_str = "N/A"

    return jsonify({
        "completed": completed_count,
        "remaining": remaining_count,
        "current_status": current_status(),
        "time_until_reset": time_until_reset_str
    })

@app.route("/rankings/model_families")
def model_family_rankings():
    """Provides data for the rankings of model families."""
    rankings = db.get_model_family_rankings()
    return jsonify(rankings)

@app.route("/rankings/models/<model_family>")
def model_rankings(model_family):
    """Provides data for the rankings of models within a specific model family."""
    rankings = db.get_model_rankings_within_family(model_family)
    return jsonify(rankings)

@app.route("/rankings/years")
def year_rankings():
    """Provides data for the rankings of puzzle years."""
    rankings = db.get_year_rankings()
    return jsonify(rankings)

@app.route("/experiments")
def experiments():
    """Provides data for all experiments"""
    all_experiments = db.get_all_experiments()
    
    # Convert experiment tuples to dictionaries for easier JSON conversion
    experiments_as_dicts = []
    for exp in all_experiments:
        exp_dict = {
            "id": exp[0],
            "model_family": exp[1],
            "model_name": exp[2],
            "year": exp[3],
            "day": exp[4],
            "part": exp[5],
            "prompt": exp[6],
            "program": exp[7],
            "result": exp[8],
            "answer": exp[9],
            "correct": exp[10],
            "timeout": exp[11],
            "start_time": exp[12],
            "end_time": exp[13],
            "error_message": exp[14],
            "previous_attempt_timed_out": exp[15]
        }
        experiments_as_dicts.append(exp_dict)
    
    return jsonify(experiments_as_dicts)

@app.route("/experiments/<int:experiment_id>")
def experiment_details(experiment_id):
    """Provides details for a specific experiment."""
    experiment = db.get_experiment_by_id(experiment_id)
    if experiment:
        return jsonify(experiment)
    else:
        return jsonify({"error": "Experiment not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)