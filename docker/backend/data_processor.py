import pandas as pd
import requests
import sqlite3
from collections import Counter
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import nltk
from nltk.corpus import stopwords
import inflect

#load_dotenv()
#API_URL=os.getenv('API_URL')
p = inflect.engine()
DATABASE = "location_cache.db"
nltk.download("stopwords")

stop_words = set(stopwords.words("english"))
additional_stop_words = ['tornado', 'hurricane', 'wildfire', 'blizzard', 'earthquake', 'flood', 'watchedskysocialappalerts']
stop_words.update((additional_stop_words))
stop_words.update({p.number_to_words(i) for i in range(0,1001)})

class DataProcessor:
    def __init__(self):

        """Fetches data once to be used across all API calls"""
        self.df = self.fetch_data()
    def fetch_data(self):

        """Fetching data from the API URL and converting to dataframe"""
        response = requests.get("http://db:5001/get_latest_posts")
    
        if response.status_code != 200:
            print(f"error: failed to fetch data with status code {response.status_code}")
            return None
        data = response.json()
        posts = data.get("posts", []) 
        return pd.DataFrame(posts)

    def filter_data(self, since=None, label=None, location=False, specific_location=None):

        """Data filtering based on what the other functions need"""
        df = self.df.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        if since:
            df = df[df["timestamp"] >= pd.to_datetime(since, utc=True)]
        if label:
            df = df[df["label"] == label]
        if location:
            df = df[df["location"].notna()]
        if specific_location:
            df = df[df["location"]==specific_location]
        return df
    
    def fetch_label_count(self):
        """Fetching the count and percentage for each label"""
        df = self.df
        count = df["label"].value_counts().to_dict() 
        total_count = df["label"].count()
        results = [
        {"label": str(label), "count": int(c), "percentage": float((c / total_count) * 100)} 
        for label, c in count.items()
        ]
        return {
            "total label count": int(total_count),
            "results": results
        }
    def fetch_most_frequent(self, disaster_type):

        """Finds the most common words based on label or over entire dataset"""
        df = self.filter_data(label=disaster_type)
        all_cleaned_text = " ".join(df["cleaned"].astype(str))
        words = [word for word in all_cleaned_text.split() if word not in stop_words and not word.isdigit() and len(word)> 3]
        count = Counter(words)
        return [{"keyword": str(word), "count": int(freq)} for word, freq in count.most_common(20)]
    
    def fetch_posts_over_time(self, disaster_type):

        """Finds the posts per day based on disaster type"""
        df = self.filter_data(label=disaster_type)
        posts_per_day = df.resample("D", on="timestamp").size().reset_index(name="post_count")
        posts_per_day["timestamp"] = posts_per_day["timestamp"].dt.strftime("%Y-%m-%d")
        
        return posts_per_day.to_dict(orient="records")

    def fetch_top_disaster_last_day(self):

        """Gets the most popular disaster type, location, and danger level within the past 24 hours"""
        last_day = datetime.utcnow() - timedelta(days=1)
        df = self.filter_data(since=last_day, location=True) #filtering by non-null locations
        if df.empty:
            return {"Error": "No valid disasters mentioned in the last day"}
        
        #Finding the most popular disaster-location pair
        top_pair = Counter(zip(df['label'], df['location'])).most_common(1)
        if not top_pair:
            return {"Error": "No valid disaster-location pairs"}
        top_label, top_location = top_pair[0][0]

        #Filter data again to get only the entries related to the pair
        df_labloc = self.filter_data(since=last_day, label=top_label, specific_location=top_location)
        df_labloc['sentiment'] = pd.to_numeric(df['sentiment'], errors='coerce')

        #Using minmax scaling to emphasize the sentiment scores more
        min_sent = df_labloc['sentiment'].min()
        max_sent = df_labloc['sentiment'].max()
        df_labloc['sentiment_scaled'] = (df_labloc['sentiment']-min_sent)/(max_sent-min_sent)

        #Danger Level calculated by mean of sentiment scores
        avg_sentiment = df_labloc['sentiment_scaled'].mean()
        if avg_sentiment <= -0.5:
            danger_level = "high"
        elif avg_sentiment < 0.5:
            danger_level = "moderate"
        else:
            danger_level = "low"

        return {
            "top_label": str(top_label), 
            "location" : str(top_location), 
            "danger_level": str(danger_level), 
            "danger_value": float(avg_sentiment)
            }

    def fetch_text_last_day(self, disaster_type):

        last_hour = datetime.utcnow() - timedelta(days=1)
        df = self.filter_data(since=last_hour, label=disaster_type)
        if df.empty:
            return {"error": "disaster type not found"}
        df['timestamp'] = df['timestamp'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if pd.notnull(x) else '')
        return df[['text', 'author', 'timestamp']].to_dict(orient="records")
    
    def fetch_location_coordinates(self):
         
        """Fetches coordinates from geocoded_cache.db"""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT latitude, longitude FROM locations")
        rows = cursor.fetchall()
        conn.close()

        return [{"latitude": row[0], "longitude": row[1]} for row in rows]
