from flask import Flask, jsonify, request
import pandas as pd
from collections import Counter
import csv
import re
import nltk
import os
from nltk.corpus import stopwords
from flask_cors import CORS
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter


app = Flask(__name__)
CORS(app)  

df = pd.read_csv('lahaina-label.tsv', sep='/t', names = ['sentiment', 'text'], skiprows = 1)
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

@app.route('/fetch-location-coordinates/', methods=['GET'])
def fetch_location_coordinates():

    #reading the csv file
    with open('locations.csv') as f:
        read_obj = csv.reader(f)
        results = []
        next(read_obj)  
        results = [tuple(row) for row in read_obj]

    geolocator = Nominatim(user_agent="city_coordinates_app")

    # Rate limiting to avoid hitting the API too fast
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, max_retries=3, error_wait_seconds=1)
    adjusted_location = []

    for result in results:
        location_name = f"{result[0]}, {result[1]}" 
        location = geocode(location_name, timeout = 10)
        if location:
            adjusted_location.append(
                {
                    'location': location_name,
                    'latitude': location.latitude,
                    'longitude': location.longitude
                }
            )
        else:
            adjusted_location.append(
                {
                   'location': location_name,
                   'latitude': 'Not Found',
                   'longitude':'Not Found' 
                }
            )
    return jsonify(adjusted_location)

@app.route('/fetch-info/', methods=['GET'])
def fetch_label_or_text():
    # Get the column name from the request arguments i.e. /fetch-info/?column_name=sentiment
    column_name = request.args.get('column_name')
    
    # Check if the column name is provided and exists in the DataFrame
    if column_name in df.columns:
        data = df[column_name].head(10).to_dict()
    else:
        data = {'error': 'Invalid or missing column name'}
    
    return jsonify(data)

#Good for a pie chart or keyword cloud
@app.route('/fetch-disaster-count/', methods = ['GET'])
def fetch_percentage():
    # Calculate the percentage of the user-typed label
    keyword = request.args.get('keyword')
    count = df['sentiment'].str.contains(keyword, case=False).sum()
    total_count = df['sentiment'].count()
    percentage = (count / total_count) * 100 
    return jsonify({'keyword': keyword,
                    'count': count,
                    'total_label_count': int(total_count),
                    'percentage': percentage}) 

#fetching most frequent for Keyword Cloud (will be subject to change when i have pre-processed data)
@app.route('/fetch-most-frequent-word/', methods = ['GET'])
def fetch_most_frequent():

    #Combining the text column as a single string
    text_combined = " ".join(df['text'].astype(str))

    #Using regex to remove punctuation, newlines, and convert to lowercase
    cleaned_text = re.sub(r'[\n\r]+', ' ', text_combined.lower())
    cleaned_text = re.sub(r'[^\w\s]', '', cleaned_text)

    #Removing all the filler words (i.e. to, and, a, etc.) in the text 
    filtered_text = [w for w in cleaned_text.split() if not w in stop_words] 

    #Counting the frequency of each word
    count = Counter(filtered_text)

    return jsonify([{'keyword': word, 'count': freq} for word, freq in count.most_common(10)])

if __name__ == '__main__':
    app.run(debug=True)