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
import redis

load_dotenv()
nltk.download("stopwords")

class DataProcessor:
    def __init__(self):
        """Fetches data once to be used across all API calls"""
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))

        self.redis_cli = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)
        self.cache_df = self.load_cache_data()
        #all timestamps should be in pd.Timestamp format 
        self.latest_timestamp = self.load_latest_timestamp()

        self.api_url = os.getenv('API_URL')
        self.location_database = os.getenv('CACHE_FILE')

        p = inflect.engine()
        self.stop_words = set(stopwords.words("english"))
        additional_stop_words = [
            'tornado', 
            'hurricane', 
            'wildfire', 
            'earthquake', 
            'flood',
            'flooding',
            'watchedskysocialappalerts', 
            'hundred',
            'thousand'
        ]
        self.stop_words.update((additional_stop_words))
        self.stop_words.update({p.number_to_words(i) for i in range(0,1001)})
        self.fetch_data()

    def load_latest_timestamp(self):
        latest_timestamp = self.redis_cli.get("latest_timestamp")
        if latest_timestamp:
            latest_ts = pd.to_datetime(latest_timestamp, utc=True)
            return latest_ts
        else:
            return None
    
    def load_cache_data(self):
        cache_data = self.redis_cli.get("cache_data")
        if cache_data:
            try:
                df = pd.read_json(cache_data)
                if "timestamp" in df.columns:
                    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
                return df
            except Exception as e:
                return pd.DataFrame()
        else:
            return pd.DataFrame()
        
    def fetch_data(self):
        """Fetching data from the API URL and converting to dataframe"""
        if self.latest_timestamp:
            timestamp = self.latest_timestamp.strftime("%Y-%m-%dT%H:%M:%S")
            response = requests.get(f"{self.api_url}/get_latest_posts?start_timestamp={timestamp}")

            if response.status_code != 200:
                return None
        else:
            response = requests.get(f"{self.api_url}/get_latest_posts") # grab everything if no latest
        
        # Update the latest timestamp
        data = response.json()
        new_latest_timestamp = pd.to_datetime(data.get("latest_timestamp"), utc=True)

        if self.latest_timestamp is None or new_latest_timestamp > self.latest_timestamp:
            self.latest_timestamp = new_latest_timestamp + timedelta(seconds=1) # so we don't grab last post
            
        posts = data.get("posts", [])
        if not posts:
            return self.cache_df
        
        new_df = pd.DataFrame(posts)
        new_df["timestamp"] = pd.to_datetime(new_df["timestamp"], utc=True)

        #Merge with existing df
        self.cache_df = pd.concat([self.cache_df, new_df], ignore_index=True)
        self.redis_cli.set("cache_data", self.cache_df.to_json(orient="records"))

        #redis stores everything as strings, so we need to convert the timestamp to a string
        self.redis_cli.set("latest_timestamp", self.latest_timestamp.strftime("%a, %d %b %Y %H:%M:%S GMT"))

        return self.cache_df

    def filter_data(self, since=None, latest=None, label=None, location=False, specific_location=None, sentiment=False):
        """Data filtering based on what the other functions need"""
        df = self.cache_df.copy() # changed to cache_df
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        if since:
            df = df[df["timestamp"] >= pd.to_datetime(since, utc=True)]
        if latest:
            df = df[df["timestamp"] < pd.to_datetime(latest, utc=True) + timedelta(days=1)]
        if label:
            df = df[df["label"] == label]
        if location:
            df = df[df["location"].notna()]
        if specific_location:
            df = df[df["location"]==specific_location]
        if sentiment:
            df['sentiment'] = pd.to_numeric(df['sentiment'], errors='coerce')
            df['sentiment_scaled'] = (df['sentiment'] - df['sentiment'].min()) / (df['sentiment'].max() - df['sentiment'].min())
        return df

    def validate_date_range(self, start_date, end_date):
        """Validating the date range as provided by user"""

        #No date range provided, default to last 24 hours
        if start_date is None and end_date is None:
            end_date = pd.to_datetime(datetime.utcnow(), utc=True)
            start_date = end_date - timedelta(days=1)
        
        #If only start_date or only end_date is provided
        if start_date and not end_date:
            end_date = self.cache_df["timestamp"].max()

        if end_date and not start_date:
            start_date = self.cache_df["timestamp"].min()
        
        #Inputed date range accepted for pd.to_datetime format
        try:
            start_date = pd.to_datetime(start_date, utc=True)
            end_date = pd.to_datetime(end_date, utc=True)
        except ValueError:
            return {"error": "Invalid date format. Enter date in YYYY-MM-DD format."} 

        if start_date > end_date:
            return {"error": "Start date must be before end date."}
        return start_date, end_date
    
    def fetch_label_count(self, start_date=None, end_date=None):
        """Fetching the count and percentage for each label"""
        df = self.cache_df # changed to cache_df
        validation = self.validate_date_range(start_date, end_date)
        if isinstance(validation, dict) and "error" in validation:
            return validation
        start_date, end_date = validation

        #filter by date range
        df = self.filter_data(since=start_date, latest=end_date)
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
    def fetch_most_frequent(self, disaster_type, start_date=None, end_date=None):
        """Finds the most common words based on label or over entire dataset"""
        validation = self.validate_date_range(start_date, end_date)
        if isinstance(validation, dict) and "error" in validation:
            return validation
        start_date, end_date = validation

        #filter by date range and disaster type
        df = self.filter_data(since=start_date, latest=end_date, label=disaster_type)
        all_cleaned_text = " ".join(df["cleaned"].astype(str))
        words = [word for word in all_cleaned_text.split() if word not in self.stop_words and not word.isdigit() and len(word)> 3]
        count = Counter(words)
        return [{"keyword": str(word), "count": int(freq)} for word, freq in count.most_common(20)]
    
    def fetch_posts_over_time(self, disaster_type, start_date=None, end_date=None):
        """Finds the posts per day based on disaster type"""
        validation = self.validate_date_range(start_date, end_date)
        if isinstance(validation, dict) and "error" in validation:
            return validation
        start_date, end_date = validation

        #filter by date range and disaster type
        df = self.filter_data(since=start_date, latest=end_date, label=disaster_type)
        if df.empty:
            return {"error": "No posts found for the given date range"}
        posts_per_day = df.resample("D", on="timestamp").size().reset_index(name="post_count")
        posts_per_day["timestamp"] = posts_per_day["timestamp"].dt.strftime("%Y-%m-%d")
        
        return posts_per_day.to_dict(orient="records")

    def fetch_top_disaster_location(self, start_date=None, end_date=None):
        """Gets the most popular disaster type, location, and danger level within the past 24 hours"""
        validation = self.validate_date_range(start_date, end_date)
        if isinstance(validation, dict) and "error" in validation:
            return validation
        start_date, end_date = validation

        #filtering by non-null locations and date range
        df = self.filter_data(since=start_date, latest=end_date, location = True) 
        if df.empty:
            return {"Error": "No valid disasters mentioned in the last day"}
        
        #Finding the most popular disaster-location pair
        top_pair = Counter(zip(df['label'], df['location'])).most_common(1)
        if not top_pair:
            return {"Error": "No valid disaster-location pairs"}
        top_label, top_location = top_pair[0][0]

        #Filter data again to get only the entries related to the pair
        df_filtered = self.filter_data(since=start_date, latest=end_date, label=top_label, specific_location=top_location, sentiment=True)

        #Danger Level calculated by mean of sentiment scores
        avg_sentiment = df_filtered['sentiment_scaled'].mean()
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

    def fetch_text(self, disaster_type, start_date=None, end_date=None):

        validation = self.validate_date_range(start_date, end_date)
        if isinstance(validation, dict) and "error" in validation:
            return validation
        start_date, end_date = validation

        #filter by date range and disaster type
        df = self.filter_data(since=start_date, latest=end_date, label=disaster_type)
        if df.empty:
            return {"error": "disaster type not found"}
        
        df['timestamp'] = df['timestamp'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if pd.notnull(x) else '')
        return df[['text', 'handle', 'timestamp']].to_dict(orient="records")
    
    def fetch_location_coordinates(self):
        """Fetches coordinates from geocoded_cache.db"""
        conn = sqlite3.connect(self.location_database)
        cursor = conn.cursor()
        cursor.execute("SELECT latitude, longitude FROM locations")
        rows = cursor.fetchall()
        conn.close()

        return [{"latitude": row[0], "longitude": row[1]} for row in rows]

