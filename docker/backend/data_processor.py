import pandas as pd
import requests
from collections import Counter
import json
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
import redis
import spacy 
from typing import Optional, Dict

load_dotenv()
nlp = spacy.load("en_core_web_sm")
#nlp.max_length = 3000000


class AtUri:
    def __init__(self, repo: str, collection: str, rkey: str):
        self.repo = repo
        self.collection = collection
        self.rkey = rkey
        
class DataProcessor:
    def __init__(self):
        """Fetches data once to be used across all API calls"""
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))

        self.redis_cli = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)
        self.cache_df = self.load_cache_data()

        #all timestamps should be in UTC format 
        self.latest_timestamp = self.load_latest_timestamp()

        self.api_url = os.getenv('API_URL')
        self.location_database = os.getenv('CACHE_FILE')

        self.additional_stop_words = set([
            'tornado', 
            'hurricane', 
            'wildfire', 
            'earthquake', 
            'flood',
            'flooding',
            'watchedskysocialappalerts', 
            'hundred',
            'thousand',
            'bskysocial',
            'iembot'
        ])
        self.full_stop_words = nlp.Defaults.stop_words.union(self.additional_stop_words)
        self.fetch_data()

        self.uri_templates: Dict[str, Dict[str, str]] = {
            "app.bsky.actor.profile": {
                "label": "Bluesky",
                "link": lambda uri: f"https://bsky.app/profile/{uri.repo}",
            },
            "app.bsky.feed.post": {
                "label": "Bluesky",
                "link": lambda uri: f"https://bsky.app/profile/{uri.repo}/post/{uri.rkey}",
            },
            "app.bsky.graph.list": {
                "label": "Bluesky",
                "link": lambda uri: f"https://bsky.app/profile/{uri.repo}/lists/{uri.rkey}",
            },
            "app.bsky.feed.generator": {
                "label": "Bluesky",
                "link": lambda uri: f"https://bsky.app/profile/{uri.repo}/feed/{uri.rkey}",
            },
            "fyi.unravel.frontpage.post": {
                "label": "Frontpage",
                "link": lambda uri: f"https://frontpage.fyi/post/{uri.repo}/{uri.rkey}",
            },
            "com.whtwnd.blog.entry": {
                "label": "WhiteWind",
                "link": lambda uri: f"https://whtwnd.com/{uri.repo}/{uri.rkey}",
            },
            "com.shinolabs.pinksea.oekaki": {
                "label": "PinkSea",
                "link": lambda uri: f"https://pinksea.art/{uri.repo}/oekaki/{uri.rkey}",
            },
            "blue.linkat.board": {
                "label": "Linkat",
                "link": lambda uri: f"https://linkat.blue/{uri.repo}",
            },
        }

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
                #df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
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
        
        #Update the latest timestamp
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

    def filter_data(self, since, latest, **kwargs):
        """Data filtering based on what the other functions need"""
        df = self.cache_df.copy() # changed to cache_df
        try:
            since = pd.to_datetime(since, utc=True)
            latest = pd.to_datetime(latest, utc=True)
        except Exception:
            raise ValueError("'since' and 'latest' must be valid datetime strings and are required paramters.")

        #all timestamps in UTC format
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        df = df[(df["timestamp"] >= since) & (df["timestamp"] < latest + timedelta(days=1))]

        label = kwargs.get("label")
        if label:
            df = df[df["label"] == label]
        
        location_column = kwargs.get("location_column")
        if location_column:
            df = df[df[location_column].notna()]

            specific_location = kwargs.get("specific_location")
            if specific_location:
                df = df[df[location_column] == specific_location]
            
            coordinates = kwargs.get("coordinates")
            if coordinates:
                df = df[df["lat"].notna() & df["lng"].notna() & (df['lat'] != 0) & (df['lng'] != 0)]
        

        df['sentiment'] = pd.to_numeric(df['sentiment'], errors='coerce')
        df['sentiment_scaled'] = (df['sentiment'] - df['sentiment'].min()) / (df['sentiment'].max() - df['sentiment'].min())
        return df

    def validate_date_range(self, start_date, end_date):
        """Validating the date range as provided by user"""

        #No date range provided, default to last 24 hours
        if start_date is None and end_date is None:
            end_date = pd.to_datetime(datetime.utcnow(), utc=True)
            start_date = end_date - timedelta(days=1)
        
        #only start_date provided 
        if start_date and not end_date:
            end_date = self.cache_df["timestamp"].max()
        
        #only end_date is provided
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
        if df.empty:
            return {"error": "No posts found for the given date range"}

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
        if df.empty:
            return {"error": "No posts found for the given date range and disaster_type"}
        all_cleaned_text = " ".join(df["cleaned"].astype(str))

        words = self.process_large_text(all_cleaned_text)
        
        count = Counter(words)
        return [{"keyword": str(word), "count": int(freq)} for word, freq in count.most_common(20)]
    
    def process_large_text(self, text, chunk_size=1000000):
        """Processes large texts in chunks to avoid memory overload."""
        chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
        words = []
        
        with nlp.disable_pipes("ner"):
            for chunk in chunks:
                doc = nlp(chunk)
                words.extend([
                    token.lemma_ for token in doc
                    if token.pos_ in ["NOUN", "PROPN"]
                    and token.text.lower() not in self.full_stop_words
                    and not token.is_punct
                    and not token.like_num
                    and len(token.lemma_) > 3
                ])
        return words

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
        ###norm_loc locations before 4/14 are null, so use the "location" column for those before that cutoff date###

        cutoff_date = datetime(2025, 4, 14, tzinfo=timezone.utc)
        if start_date >= cutoff_date:
            location_column = "norm_loc"
        else:
            location_column = "location"

        df = self.filter_data(since=start_date, latest=end_date, location_column=location_column) 
        print("Filtered DataFrame shape:", df.shape)
        print("Top 5 rows:")
        print(df[['label', location_column, 'sentiment']].head())
        if df.empty:
            return {"Error": "No valid disasters mentioned in the given date range"}
        
        #Finding the most popular disaster-location pair
        top_pair = Counter(zip(df['label'], df[location_column])).most_common(1)
        if not top_pair:
            return {"Error": "No valid disaster-location pairs"}
        top_label, top_location = top_pair[0][0]

        #Filter data again to get only the entries related to the pair
        df_filtered = self.filter_data(since=start_date, latest=end_date, label=top_label, specific_location=top_location)

        #Danger Level calculated by mean of sentiment scores
        avg_sentiment = df_filtered['sentiment'].mean()
        if pd.isna(avg_sentiment):
            return {
            "top_label": str(top_label),
            "location": str(top_location),
            "danger_level": "unknown",
            "danger_value": None
            }
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

    def check_uri(self, uri_str):
        if uri_str is None:
            return None
        
        parts = str(uri_str).split("/")
        if len(parts) != 5 or parts[0] != "at:" or parts[1] != "":
            return None

        uri = AtUri(repo=parts[2], collection=parts[3], rkey=parts[4])
        template = self.uri_templates.get(uri.collection)

        if not template:
            return None

        return {
            "label": template["label"],
            "link": template["link"](uri),
        }


    def fetch_text(self, disaster_type, start_date=None, end_date=None):

        validation = self.validate_date_range(start_date, end_date)
        if isinstance(validation, dict) and "error" in validation:
            return validation
        start_date, end_date = validation

        #filter by date range and disaster type
        df = self.filter_data(since=start_date, latest=end_date, label=disaster_type)
        if df.empty:
            return {"error": "No posts found for the given date range"}

        df['timestamp'] = df['timestamp'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if pd.notnull(x) else '')
        df['url'] = df['id'].apply(lambda x: self.check_uri(x)['link'] if pd.notnull(x) else '')
        return df[['text', 'handle', 'timestamp', 'url']].to_dict(orient="records")
    
    def fetch_location_coordinates(self, disaster_type, start_date=None, end_date=None):

        """Fetches coordinates based on label and optional date range"""
        validation = self.validate_date_range(start_date, end_date)
        if isinstance(validation, dict) and "error" in validation:
            return validation
        start_date, end_date = validation

        #filter by date range and disaster type
        df = self.filter_data(since=start_date, latest=end_date, label=disaster_type, location_column="norm_loc", coordinates=True)
        if df.empty:
            return {"error": f"only invalid locations for {disaster_type} found"}

        return df[['norm_loc', 'lat', 'lng', 'sentiment']].to_dict(orient="records")
        
        

