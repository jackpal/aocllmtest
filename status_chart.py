import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from db_util import create_or_open_puzzle_db

def create_stacked_status_chart_2024(db_name="puzzle.db"):
    """
    Creates a horizontal stacked bar chart showing the percentage of correct, incorrect,
    timeout, and error answers for each model in the year 2024.
    The bars are stacked in the order: correct, incorrect, timeout, error.
    Models are sorted by the number of correct answers.
    Percentages are calculated based on the total number of possible puzzles (49).
    """
    conn = create_or_open_puzzle_db(db_name)

    # Query to get data for 2024 only
    query = """
        SELECT
            model_name,
            CASE
                WHEN answer_is_correct = 1 THEN 'correct'
                WHEN answer_is_correct = 0 THEN 'incorrect'
                WHEN run_status = 'timeout' THEN 'timeout'
                WHEN run_status = 'error' THEN 'error'
                ELSE 'not_attempted'
            END as status
        FROM Experiments
        WHERE puzzle_year = 2024
    """

    # Load data into pandas DataFrame
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Group by model and status, then calculate the size of each group
    df_grouped = df.groupby(['model_name', 'status']).size().reset_index(name='count')

    # Pivot the table to get it into the right format for a stacked bar chart
    df_pivot = df_grouped.pivot_table(index='model_name', columns='status', values='count', fill_value=0)

    # Define the desired order for status categories
    status_order = ['correct', 'incorrect', 'timeout', 'error']

    # Reorder the columns for stacking order and fill NaN values with 0
    df_pivot = df_pivot.reindex(columns=status_order, fill_value=0)

    # Calculate percentages based on the total number of possible puzzles (49)
    df_pivot = df_pivot.apply(lambda x: (x / 49) * 100, axis=1)

    # Sort by correct percentage for better visualization
    df_pivot.sort_values(by=['correct', 'incorrect', 'timeout', 'error'], inplace=True)

    # Create the stacked bar plot using pandas plotting
    plt.figure(figsize=(14, 8))
    sns.set_theme(style="whitegrid")

    # Plot the data
    ax = df_pivot.plot(kind='barh', stacked=True, color=sns.color_palette("Set2"), ax=plt.gca())

    # Customize the plot
    ax.set_title('One-shot Model Performance 2024', fontsize=16)
    ax.set_xlabel('Puzzles %', fontsize=14)
    ax.set_ylabel('Model Name', fontsize=14)
    ax.legend(title='Status', title_fontsize='13', loc='lower right')

    # Add value labels to the bars, only if the value is >= 0.1%
    for container in ax.containers:
        labels = [f'{w:.1f}' if (w := v.get_width()) >= 0.1 else '' for v in container]
        ax.bar_label(container, labels=labels, label_type='center')

    plt.tight_layout()
    plt.savefig("one_shot_model_performance_2024.png")
    plt.show()

if __name__ == "__main__":
    create_stacked_status_chart_2024()
