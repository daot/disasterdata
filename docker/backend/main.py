from flask import Flask, jsonify, request
import pandas as pd
from collections import Counter
import csv
import re
import nltk
import os
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter


app = Flask(__name__)

df = pd.read_csv(
    "merged-reduced.tsv",
    sep="\t",
    names=["id", "author", "handle", "timestamp", "query", "text", "label"],
    skiprows=1,
)

nltk.download("stopwords")
nltk.download("punkt_tab")
nltk.download('wordnet')
stop_words = set(stopwords.words("english"))
additional_stopwords = ["ha", "going", "like", "get", "got", "today", "still", "itu2019s", "go"]
updated_stop_words = stop_words.union(set(additional_stopwords))
lemmatizer = WordNetLemmatizer()

@app.route("/fetch-location-coordinates/", methods=["GET"])
def fetch_location_coordinates():

    # reading the csv file
    with open("locations.csv") as f:
        read_obj = csv.reader(f)
        results = []
        next(read_obj)
        results = [tuple(row) for row in read_obj]

    geolocator = Nominatim(user_agent="city_coordinates_app")

    # Rate limiting to avoid hitting the API too fast
    geocode = RateLimiter(
        geolocator.geocode, min_delay_seconds=1, max_retries=3, error_wait_seconds=1
    )
    adjusted_location = []

    for result in results:
        location_name = f"{result[0]}, {result[1]}"
        location = geocode(location_name, timeout=10)
        if location:
            adjusted_location.append(
                {
                    "location": location_name,
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                }
            )
        else:
            adjusted_location.append(
                {
                    "location": location_name,
                    "latitude": "Not Found",
                    "longitude": "Not Found",
                }
            )
    return jsonify(adjusted_location)


@app.route("/fetch-data-from-label/", methods=["GET"])
def fetch_data_from_label():
    # Get the column name from the request arguments i.e. /fetch-info/?label=tornado (DON'T PUT IN QUOTES)
    label = request.args.get("label")

    #label choices are ['other' 'tornado' 'flood' 'wildfire' 'hurricane' 'blizzard']
    #print(df["label"].unique())

    df['label'] = df['label'].astype(str)

    label_data = df[df['label'] == label]

    if label_data.empty:
        return jsonify({"Error": "Label not found"})

    filter_data = label_data.to_dict(orient="records")
    return jsonify(filter_data)


# Good for a pie chart or keyword cloud
@app.route("/fetch-label-count/", methods=["GET"])
def fetch_percentage():
    # Options are ['other' 'tornado' 'flood' 'wildfire' 'hurricane' 'blizzard']
    keyword = request.args.get("keyword")
    if not keyword:
        return jsonify({"Error": "Keyword not provided"}), 400
    
    df_filtered = df["label"].dropna().astype(str)
    count = df_filtered.str.contains(str(keyword), case=False).sum()
    total_count = df["label"].count()
    percentage = (count / total_count) * 100
    return jsonify(
        {
            "keyword": keyword,
            "count": int(count),
            "total_label_count": int(total_count),
            "percentage": float(percentage),
        }
    )

# fetching most frequent for keyword Cloud (will be subject to change when i have pre-processed data)
#to fix the unicode issue, i can maybe use ensure_ascii on the df before processing for count
@app.route("/fetch-most-frequent-word/", methods=["GET"])
def fetch_most_frequent():
    disaster_type = request.args.get("disaster_type")
    if disaster_type is None:
        filtered_df = df
    else:
        filtered_df = df[df["label"]==disaster_type]

    if filtered_df.empty:
        return jsonify({"error": "error processing data"}), 404

    # Combining the text column as a single string
    text_combined = " ".join(filtered_df["text"].astype(str))

    #Using regex to remove punctuation, newlines, and convert to lowercase
    cleaned_text = re.sub(r"[\n\r]+", " ", text_combined.lower())
    cleaned_text = re.sub(r"[^\w\s]", "", cleaned_text)

    tokens = word_tokenize(cleaned_text)

    lemmatized_words = [lemmatizer.lemmatize(word) for word in tokens]

    # Removing all the filler words (i.e. to, and, a, etc.) in the text
    filtered_text = [w for w in cleaned_text if not w in updated_stop_words]

    # Counting the frequency of each word
    count = Counter(filtered_text)
    return jsonify(
        [{"keyword": str(word), "count": int(freq)} for word, freq in count.most_common(20)]
    )



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
