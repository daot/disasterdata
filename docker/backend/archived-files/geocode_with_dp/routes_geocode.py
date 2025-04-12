from flask import Flask, jsonify, request, Response
from data_processor import DataProcessor
import json
import asyncio
import logging
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
process = DataProcessor()

logging.basicConfig(
    filename="api_debug.log",
    level=logging.DEBUG,
    filemode="w",
    format="%(asctime)s %(message)s"
)

@app.route("/fetch-label-count", methods=["GET"])
def label_count():
    return jsonify(process.fetch_label_count())

@app.route("/fetch-most-frequent-word", methods=["GET"])
def most_frequent():
    disaster_type = request.args.get("disaster_type")
    return jsonify(process.fetch_most_frequent(disaster_type))

@app.route("/fetch-posts-over-time")
def posts_time():
    disaster_type = request.args.get("disaster_type")
    if not disaster_type:
        return jsonify({"error": "label must be provided"}), 400
    return jsonify(process.fetch_posts_over_time(disaster_type))

@app.route("/fetch-top-disaster-last-day", methods = ["GET"])
def top_disaster():
    return jsonify(process.fetch_top_disaster_last_day())

@app.route("/fetch-text-from-label", methods=["GET"])
def view_feed_data():
    disaster_type = request.args.get("disaster_type")
    return Response(
        json.dumps(process.fetch_text_last_day(disaster_type), ensure_ascii=False, indent=4),
        mimetype='application/json'
    )
    
@app.route('/fetch-location-coordinates')
def fetch_coordinates():
    """API endpoint to retrieve location coordinates from Redis cache or Database cache"""
    disaster_type = request.args.get("disaster_type")
    if not disaster_type:
        return jsonify({"error": "disaster_type parameter is required"}), 400

    logging.info(f"Fetching location coordinates for disaster type: {disaster_type}")
    
    try:
        result = asyncio.run(process.fetch_location_coordinates(disaster_type))
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error fetching coordinates: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)