import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from db_util import create_or_open_puzzle_db

def create_yearly_performance_chart(db_name="puzzle.db"):
    """
    Creates a line plot showing the performance of each model per year,
    where the y-axis is the percentage of correct answers and the x-axis is the contest year.
    Uses different line styles based on model categories.
    """
    conn = create_or_open_puzzle_db(db_name)

    # Query to get data for all years
    query = """
        SELECT
            model_name,
            puzzle_year,
            CAST(SUM(CASE WHEN answer_is_correct = 1 THEN 1 ELSE 0 END) AS REAL) * 100 / 49 as correct_percentage
        FROM Experiments e
        GROUP BY model_name, puzzle_year
        ORDER BY puzzle_year, model_name
    """

    # Load data into pandas DataFrame
    df = pd.read_sql_query(query, conn)

    conn.close()

    # Define model categories based on substrings in model_name
    def get_model_category(model_name):
        if "gemini" in model_name.lower():
            return "Gemini"
        elif "gemma" in model_name.lower():
            return "Gemma"
        elif "llama" in model_name.lower():
            return "LLaMA"
        elif "qwen" in model_name.lower():
            return "Qwen"
        else:
            return "Other"

    # Add a 'model_category' column to the DataFrame
    df['model_category'] = df['model_name'].apply(get_model_category)

    # Define line styles for each category
    line_styles = {
        "Gemini": "",  # Solid
        "Gemma": (2, 2),  # Dashed
        "LLaMA": (4, 1, 1, 1),  # Dash-dot-dot
        "Qwen": (3, 1, 3, 1),  # Dotted
        "Other": (5, 1)  # Dense dash
    }

    # Create a list of unique model categories to ensure all categories are in the style_order
    style_order = list(line_styles.keys())

    # Create the line plot using seaborn
    plt.figure(figsize=(14, 8))
    sns.set_theme(style="whitegrid")

    # Pass style_order and dashes to lineplot
    ax = sns.lineplot(
        x='puzzle_year',
        y='correct_percentage',
        hue='model_name',
        style='model_category',  # Use different line styles based on category
        data=df,
        markers=True,
        palette="tab10",
        style_order=style_order,  # Ensure all categories are included in the style mapping
        dashes=line_styles  # Use the custom line styles
    )

    # Customize the plot
    ax.set_title('Model Performance Over the Years', fontsize=16)
    ax.set_xlabel('Year', fontsize=14)
    ax.set_ylabel('Percentage of Correct Answers', fontsize=14)
    ax.legend(title='Model', title_fontsize='13', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Set y-axis limits to 0-100 for percentage
    ax.set_ylim([0, 100])

    # Format y-axis ticks as percentages
    ax.yaxis.set_major_formatter(plt.FuncFormatter('{:.0f}%'.format))

    plt.tight_layout()
    plt.savefig("yearly_model_performance.png")
    plt.show()

if __name__ == "__main__":
    create_yearly_performance_chart()
