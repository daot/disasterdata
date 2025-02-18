from flask import Flask, send_file, jsonify
from flask_cors import CORS
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend
import matplotlib.pyplot as plt
import seaborn as sb
import plotly.express as px
import sqlite3


app = Flask(__name__)
CORS(app)

"""def generate_sentiment_plot():
    conn = sqlite3.connect("./backend/posts-lahaina copy.db")
    df = pd.read_sql_query("SELECT * FROM posts", conn)
    #cursor = conn.cursor()
    print("success connection")
    #cursor.execute("SELECT * FROM posts;")
    #dataset = cursor.fetchall()
    conn.close()

    print(df.head())
    
    plt.figure(figsize=(10,6))
    sb.histplot(df['Sentiment'], kde=True, bins=30, color='blue')
    plt.title('Sentiment Distribution')
    plt.xlabel('Sentiment')
    plt.ylabel('Frequency')
    
    image_path = "sentiment_plot.png"
    plt.savefig(image_path)
    plt.close()
    
    return image_path
@app.route('/sent-plot')
def sentiment_plot():
    image_path = generate_sentiment_plot()
    return send_file(image_path, mimetype='image/png')
    generate_sentiment_plot()

@app.route('/')
def test():
    conn = sqlite3.connect("./backend/posts-lahaina copy.db")
    print("Success")
    df = pd.read_sql_query("SELECT * FROM posts", conn)
    print(df.head())
    return jsonify(df.to_dict(orient="records"))
"""
#@app.route('/scatter-plot')
#fig = px.scatter

def generate_scatter_plot():
    conn = sqlite3.connect("posts-lahaina copy.db")
    df = pd.read_sql_query("SELECT * FROM posts", conn)
    conn.close()

    df["word_count"] = df["text"].apply(lambda x: len(x.split()))
    #df["timestamp"] = pd.to_datetime(df["timestamp"], format = "ISO8601")
    df["sentiment"] = df["sentiment"].astype(float)
    #df["hour"] = df["timestamp"].dt.hour
    #df["date"] = df["timestamp"].dt.date
    fig = px.scatter(df, 
                     x="word_count", 
                     y="sentiment", 
                     color='sentiment', 
                     title='Word Count vs. Sentiment', 
                     labels= {'word_count': 'Word Count', 'sentiment': 'Sentiment'})
    return fig.to_html()

@app.route('/scatter-plot', methods=['GET'])
def scatter_plot():
    plot_html = generate_scatter_plot()
    return plot_html
if __name__ == '__main__':
    app.run(debug=True)
