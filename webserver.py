# webserver.py
from flask import Flask, render_template, jsonify
import db

app = Flask(__name__)

@app.route("/")
def index():
    """Renders the main page of the web application."""
    return render_template("index.html")

@app.route("/status")
def status():
    """Provides data for the status of the experiments."""
    completed_count, remaining_count = db.count_experiments()
    return jsonify({
        "completed": completed_count,
        "remaining": remaining_count
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
    
    return jsonify(all_experiments)

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