from flask import Flask, jsonify, request, Response
from data_processor import DataProcessor
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
process = DataProcessor()

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
    
@app.route("/fetch-location-coordinates", methods=["GET"])
def fetch_coordinates():
    """API endpoint to return coordinates from geocoded_cache.db"""
    try:
        coordinates = process.fetch_location_coordinates()
        return jsonify(coordinates)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
