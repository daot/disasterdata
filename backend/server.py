from flask import Flask, send_file, jsonify, request, render_template, url_for
from flask_cors import CORS
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb
#import plotly.express as px
import sqlite3
import os

app = Flask(__name__)
CORS(app)

# Ensure static directory exists
STATIC_DIR = "static/images"
os.makedirs(STATIC_DIR, exist_ok=True)

IMAGE_PATH_HISTOGRAM = os.path.join(STATIC_DIR, "sentiment_plot.png")
IMAGE_PATH_SCATTER = os.path.join(STATIC_DIR, "scatter_plot.png")

# Fetch data from the database
def fetch_data():
    conn = sqlite3.connect("posts-lahaina.db")
    df = pd.read_sql_query("SELECT * FROM posts", conn)
    conn.close()
    return df

# Generate histogram and save it in the static folder
def generate_histogram(df):
    plt.figure(figsize=(10, 6))
    sb.histplot(df['sentiment'], kde=True, bins=30, color='blue')
    plt.title('Sentiment Distribution')
    plt.xlabel('Sentiment')
    plt.ylabel('Frequency')

    plt.savefig(IMAGE_PATH_HISTOGRAM)  # Save in the static folder
    plt.close()
    return IMAGE_PATH_HISTOGRAM

# Generate scatter plot and save it in the static folder
def generate_scatter_plot(df):
    df.dropna()
    plt.figure(figsize=(10, 6))
    df['word_count'] = df['text'].apply(lambda x: len(x.split()))
    df['sentiment'] = df['sentiment'].astype(float)
    sb.scatterplot(data=df, x='word_count', y='sentiment', color='blue')
    plt.title('Word Count vs Sentiment')
    plt.xlabel('Word Count')
    plt.ylabel('Sentiment')

    plt.savefig(IMAGE_PATH_SCATTER)  # Save in the static folder
    plt.close()
    return IMAGE_PATH_SCATTER
def generate_scatter_plot():
    """df.dropna()
    df["word_count"] = df["text"].apply(lambda x: len(x.split()))
    df["sentiment"] = df["sentiment"].astype(float)
    fig = px.scatter(df, 
                     x="word_count", 
                     y="sentiment", 
                     color='sentiment', 
                     title='Word Count vs. Sentiment', 
                     labels= {'word_count': 'Word Count', 'sentiment': 'Sentiment'},
                     color_continuous_scale="Viridis")"""

# Load data and generate visualizations on startup
dataframe = fetch_data()
generate_histogram(dataframe)
#generate_scatter_plot(dataframe)

@app.route('/')
def index():
    histogram_file = url_for('static', filename='images/sentiment_plot.png')
    scatter_file = url_for('static', filename='images/scatter_plot.png')
    return render_template('index.html', histogram_file=histogram_file, scatter_file=scatter_file)
"""@app.route('/scatter-plot', methods=['GET'])
def scatter_plot():
    #return jsonify(generate_scatter_plot(dataframe))
    return generate_scatter_plot()"""
if __name__ == '__main__':
    app.run(debug=True)
