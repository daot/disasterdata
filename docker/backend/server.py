import pandas as pd
import requests
from flask import Flask, jsonify, request
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from collections import Counter
from datetime import datetime

app = Flask(__name__)
response = requests.get("http://disasterdata.duckdns.org:5001/get_latest_posts")

def fetch_and_convert():
    if response.status_code == 200:
        data = response.json()
        posts = data.get("posts", [])
        df = pd.DataFrame(posts)
        return df
    else:
        return None

#Validating whether it converts to df
@app.route('/get-df/', methods=["GET"])
def get_df():
    df = fetch_and_convert()
    if df is None:
        return jsonify({"Error": "Failed to fetch data"}), 500
    return jsonify(df.to_dict(orient="records"))

#Note: times out with requests > 5, may need to use something other than Nominatim
@app.route("/fetch-location-coordinates/", methods=["GET"])
def fetch_location_coordinates():
    df = fetch_and_convert()

    #Filtering out the "location = null" values
    filtered_rows = [row._asdict() for row in df.itertuples() if row.location is not None]
    new_df = pd.DataFrame(filtered_rows)
    new_df.head(5)
    """return jsonify(temp_df.to_dict(orient="records"))"""

    geolocator = Nominatim(user_agent="geo_convert", timeout=10)

    #Rate limiting to avoid hitting the API too fast
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    new_df['temp_location'] =  new_df['location'].apply(geocode)
    new_df['latitude'] =  new_df['temp_location'].apply(lambda loc: loc.latitude)
    new_df['longitude'] = new_df['temp_location'].apply(lambda loc: loc.longitude)

    new_df.drop(columns=['temp_location'], inplace=True)

    return jsonify(new_df.to_dict(orient='records'))

#API endpoint to get the ratio of posts labeled with each label
@app.route("/fetch-label-count/", methods=["GET"])
def fetch_label_count():
    # ['other' 'tornado' 'flood' 'wildfire' 'hurricane' 'blizzard'] are labels
    df = fetch_and_convert()
    count = df["label"].dropna().astype(str).value_counts().to_dict()
    total_count = df["label"].count()
    results = []
    for label, c in count.items():
        results.append(
            {
                "label": str(label),
                "count": int(c),
                "percentage": float((c / total_count) * 100)
            }
        )
    return jsonify(
        {
            "total label count": int(total_count),
            "results": results
        }
    )

#API endpoint to get most frequent words of text
@app.route("/fetch-most-frequent-word/", methods=["GET"])
def fetch_most_frequent():

    df = fetch_and_convert()
    # disaster_type is optional, but you can only search ['tornado' 'flood' 'wildfire' 'hurricane' 'blizzard']
    disaster_type = request.args.get("disaster_type")

    # make info disaster specific or of everything
    if disaster_type is None:
        filtered_df = df
    else:
        filtered_df = df[df["label"]==disaster_type]

    if filtered_df.empty:
        return jsonify({"error": "disaster type not found"}), 404
    all_cleaned_text = " ".join(filtered_df["cleaned"].astype(str))
    count = Counter(all_cleaned_text.split())

    return jsonify(
        [{"keyword": str(word), "count": int(freq)} for word, freq in count.most_common(20)]
    )

#API endpoint to give the number of posts per day related to a label
@app.route("/fetch-posts-over-time/")
def fetch_posts_over_time():
    df = fetch_and_convert()

    label = request.args.get("label")
    if not label:
        return jsonify({"error": "label must be provided"}), 400

    filtered_df = df[df["label"]==label]
    if filtered_df.empty:
        return jsonify({})
    
    #Convert from string to datetime object to be accepted by resample
    filtered_df["timestamp"] = pd.to_datetime(filtered_df["timestamp"], utc=True)

    #Counting the number of posts by day
    posts_per_day = filtered_df.resample("D", on="timestamp").size().reset_index(name="post_count")

    #Convert into string format
    posts_per_day["timestamp"] = posts_per_day["timestamp"].dt.strftime("%Y-%m-%d")
    return jsonify(posts_per_day.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
