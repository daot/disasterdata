#keep in mind: fix logic for the if (r.dbsize() < 60754) part; repeats for every location call

import pandas as pd
import requests
import sqlite3
from collections import Counter
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import nltk
import redis
from geocode_data_processor import get_coordinates
from nltk.corpus import stopwords
import inflect
import asyncio

load_dotenv()
API_URL=os.getenv('API_URL')
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
        response = requests.get(API_URL+"/get_latest_posts")
    
        if response.status_code != 200:
            print(f"error: failed to fetch data with status code {response.status_code}")
            return None
        data = response.json()
        posts = data.get("posts", []) 
        return pd.DataFrame(posts)

    def filter_data(self, since=None, label=None, location=False, specific_location=None, sentiment=False):

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
        if sentiment:
            df['sentiment'] = pd.to_numeric(df['sentiment'], errors='coerce')
            df = df[(df['sentiment']-df["sentiment"].min())/(df["sentiment"].max()-df["sentiment"].min())]
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
        df_labloc = self.filter_data(since=last_day, label=top_label, specific_location=top_location, sentiment=True)
        df_labloc['sentiment'] = pd.to_numeric(df_labloc['sentiment'], errors='coerce')

        #Using minmax scaling to emphasize the sentiment scores more
        min_sent = df_labloc['sentiment'].min()
        max_sent = df_labloc['sentiment'].max()
        df_labloc['sentiment_scaled'] = (df_labloc['sentiment']-min_sent)/(max_sent-min_sent)

        #Danger Level calculated by mean of sentiment scores
        avg_sentiment = df_labloc['sentiment_scaled'].mean()
        #avg_sentiment = df_labloc['sentiment'].mean()
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

        last_day = datetime.utcnow() - timedelta(days=1)
        df = self.filter_data(since=last_day, label=disaster_type)
        if df.empty:
            return {"error": "disaster type not found"}
        df['timestamp'] = df['timestamp'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if pd.notnull(x) else '')
        return df[['text', 'author', 'timestamp']].to_dict(orient="records")

    async def fetch_location_coordinates(self, disaster_type):

        """Fetches the coordinates for the locations based on the disaster type"""
        #Tested with a small subset of data, works fine
        last_hour = datetime.utcnow() - timedelta(days=1)
        df = self.filter_data(label=disaster_type, since=last_hour, location=True)
        if df.empty:
            return {"error": "disaster type not found"}

        tasks = [get_coordinates(loc) for loc in df['location']]
        coords = await asyncio.gather(*tasks)

        #df["location"] = [c[0] if c else None for c in coords]
        df["latitude"] = [c[0] if c else None for c in coords]
        df["longitude"] = [c[1] if c else None for c in coords]

        return df[["location", "latitude", "longitude", "sentiment"]].to_dict(orient="records")
        
        
        
