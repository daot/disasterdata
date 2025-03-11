import pandas as pd
import requests
from collections import Counter
from datetime import datetime, timedelta

class DataProcessor:
    def __init__(self):

        """Fetches data once to be used across all API calls"""
        self.df = self.fetch_data()
    def fetch_data(self):

        """Fetching data from the API URL and converting to dataframe"""
        response = requests.get("http://disasterdata.duckdns.org:5001/get_latest_posts")
    
        if response.status_code != 200:
            print(f"error: failed to fetch data with status code {response.status_code}")
            return None
        data = response.json()
        posts = data.get("posts", []) 
        return pd.DataFrame(posts)

    def filter_data(self, since=None, label=None):

        """Data filtering based on what the other functions need"""
        df = self.df.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        if since:
            #posts = [post for post in posts if post.get("timestamp") >= since]
            df = df[df["timestamp"] >= pd.to_datetime(since, utc=True)]
        if label:
            df = df[df["label"] == label]
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
        stop_words = ['and', 'tornado', 'hurricane', 'blizzard', 'flood', 'wildfire']
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

    def fetch_top_disaster_last_day(self):

        """Gets the most popular disaster type and location within the past 24 hours"""
        last_day = datetime.utcnow() - timedelta(days=1)
        df = self.filter_data(since=last_day)
        if df.empty:
            return {"Label": "No disasters mentioned in the last day"}
        
        count_label = Counter(df["label"])
        top_label = count_label.most_common(1)[0][0]

        count_location = Counter(df["location"])
        top_location = count_location.most_common(1)[0][0] if count_location else None
        
        return {"top_label": str(top_label),"top_location": str(top_location)}