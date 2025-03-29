import pandas as pd
import requests
from collections import Counter
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import asyncio
import aiohttp

#load_dotenv()
#API_URL=os.getenv('API_URL')

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

    def filter_data(self, since=None, label=None, location=False):

        """Data filtering based on what the other functions need"""
        df = self.df.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        if since:
            df = df[df["timestamp"] >= pd.to_datetime(since, utc=True)]
        if label:
            df = df[df["label"] == label]
        if location:
            filtered_rows = [row._asdict() for row in df.itertuples() if row.location is not None]
            new_df = pd.DataFrame(filtered_rows)
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
        stop_words = ['and', 'tornado', 'hurricane', 'blizzard', 'flood', 'wildfire', 'earthquake']
        all_cleaned_text = " ".join(df["cleaned"].astype(str))
        words = [word for word in all_cleaned_text.split() if word not in stop_words]
        count = Counter(words)
        return [{"keyword": str(word), "count": int(freq)} for word, freq in count.most_common(20)]
    
    def fetch_posts_over_time(self, disaster_type):

        """Finds the posts per day based on disaster type"""
        df = self.filter_data(label=disaster_type)
        posts_per_day = df.resample("D", on="timestamp").size().reset_index(name="post_count")
        posts_per_day["timestamp"] = posts_per_day["timestamp"].dt.strftime("%Y-%m-%d")
        return posts_per_day.to_dict(orient="records")

    def fetch_top_disaster_last_hour(self):

        """Gets the most popular disaster type and location within the past 24 hours"""
        last_hour = datetime.utcnow() - timedelta(hours=1)
        df = self.filter_data(since=last_hour)
        if df.empty:
            return {"Label": "No disasters mentioned in the last day"}

        """Counting the most common label"""
        top_label = Counter(df["label"]).most_common(1)[0][0]

        """Counting the most common location"""
        valid_locations = df["location"].dropna()
        if valid_locations.empty:
            top_location = "unknown"
        else:
            top_location = Counter(valid_locations).most_common(1)[0][0]

        return {"top_label": str(top_label), "location" : str(top_location)}

    def fetch_text_last_hour(self, disaster_type):
        #print(f"The columns of data frame are: {self.df.columns}")
        last_hour = datetime.utcnow() - timedelta(hours=1)
        df = self.filter_data(since=last_hour, label=disaster_type.lower())
        #print("Filtered data type:", type(df))
        """if df.empty:
            return {"error": "disaster type not found"}"""
        df['timestamp'] = df['timestamp'].apply(lambda x: x.strftime('%a, %b %d, %Y %H:%M:%S') if pd.notnull(x) else '')
        result = df[['text', 'author', 'timestamp']].to_dict(orient="records")
        return result



        
 
