import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from db_util import create_or_open_puzzle_db

def create_performance_chart(db_name="puzzle.db"):
    """
    Creates a bar chart showing the relative performance of different models,
    ranked by percentage of correct answers, for the year 2024 and all other years averaged.
    """
    conn = create_or_open_puzzle_db(db_name)

    # Query to get data for 2024
    query_2024 = """
        SELECT model_name, 
               CAST(SUM(CASE WHEN answer_is_correct = 1 THEN 1 ELSE 0 END) AS REAL) * 100 / 49 as correct_percentage
        FROM Experiments
        WHERE puzzle_year = 2024
        GROUP BY model_name
    """

    # Query to get data for all other years (excluding 2024)
    query_other_years = """
        SELECT model_name, AVG(correct_percentage) as correct_percentage
        FROM (
            SELECT model_name, puzzle_year, 
                   CAST(SUM(CASE WHEN answer_is_correct = 1 THEN 1 ELSE 0 END) AS REAL) * 100 / 49 as correct_percentage
            FROM Experiments
            WHERE puzzle_year <> 2024
            GROUP BY model_name, puzzle_year
        ) AS yearly_correct_percentages
        GROUP BY model_name
    """

    # Load data into pandas DataFrames
    df_2024 = pd.read_sql_query(query_2024, conn)
    df_other_years = pd.read_sql_query(query_other_years, conn)

    conn.close()

    # Add a year column to each DataFrame
    df_2024['year'] = '2024'
    df_other_years['year'] = 'Previous Years'

    # Concatenate the DataFrames
    df = pd.concat([df_2024, df_other_years])

    # Sort by correct percentage (descending) for ranking
    df.sort_values(by=['year', 'correct_percentage'], ascending=[True, False], inplace=True)

    # Create the bar plot using seaborn
    plt.figure(figsize=(12, 8))  # Adjust figure size for better readability
    sns.set_theme(style="whitegrid")  # Use a professional style

    ax = sns.barplot(
        x='correct_percentage',
        y='model_name',
        hue='year',
        data=df,
        palette="Set2",  # Choose a visually appealing color palette
        orient='h'  # Horizontal orientation for better label readability
    )

    # Customize the plot
    ax.set_title('Model Performance Comparison (Ranked by Correct Percentage)', fontsize=16)
    ax.set_xlabel('Percentage of Correct Answers', fontsize=14)
    ax.set_ylabel('Model Name', fontsize=14)
    ax.legend(title='Contest Year', title_fontsize='13', loc='lower right')

    # Add value labels to the bars using bar_label
    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f%%', label_type='edge', padding=3)

    plt.tight_layout()  # Adjust layout to prevent labels from overlapping
    plt.savefig("overall_model_performance.png")  # Save the plot as an image file
    plt.show()

if __name__ == "__main__":
    create_performance_chart()
