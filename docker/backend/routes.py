from flask import Flask, jsonify, request, Response
from flask_apscheduler import APScheduler
from data_processor import DataProcessor
import json
import asyncio
from flask_cors import CORS
import logging
import sys

app = Flask(__name__)
CORS(app)
logger = logging.getLogger(__name__)
process = DataProcessor()
scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.init_app(app)

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

@scheduler.task('interval', id='get_new_posts', seconds=60, misfire_grace_time=900)
def update_cache():
    logger.info("Update cache process started")
    process.fetch_data()
    print('Fetched data')

scheduler.start()

#127.0.0.1:5000/route_name?(start_date)=YYYY-MM-DD&(end_date)=YYYY-MM-DD&(disaster_type)=... is the format for the API calls
@app.route("/fetch-label-count", methods=["GET"])
def label_count():
    start_date = request.args.get("start_date", default=None)
    end_date = request.args.get("end_date", default=None)
    return jsonify(process.fetch_label_count(start_date, end_date))

@app.route("/fetch-most-frequent-word", methods=["GET"])
def most_frequent():
    start_date = request.args.get("start_date", default=None)
    end_date = request.args.get("end_date", default=None)
    disaster_type = request.args.get("disaster_type")
    if not disaster_type:
        return jsonify({"error": "disaster_type parameter must be provided"}), 400
    if disaster_type not in ["flood", "wildfire", "earthquake", "hurricane", "tornado"]:
        return jsonify({"error": "disaster_type parameter must be one of the following: flood, wildfire, earthquake, hurricane, tornado"}), 400
    return jsonify(process.fetch_most_frequent(disaster_type, start_date, end_date))

@app.route("/fetch-posts-over-time", methods=["GET"])
def posts_time():
    start_date = request.args.get("start_date", default=None)
    end_date = request.args.get("end_date", default=None)
    disaster_type = request.args.get("disaster_type")
    if not disaster_type:
        return jsonify({"error": "disaster_type parameter must be provided"}), 400
     if disaster_type not in ["flood", "wildfire", "earthquake", "hurricane", "tornado"]:
        return jsonify({"error": "disaster_type parameter must be one of the following: flood, wildfire, earthquake, hurricane, tornado"}), 400
    return jsonify(process.fetch_posts_over_time(disaster_type, start_date, end_date))

@app.route("/fetch-top-disaster-location", methods=["GET"])
def top_disaster():
    start_date = request.args.get("start_date", default=None)
    end_date = request.args.get("end_date", default=None)
    return jsonify(process.fetch_top_disaster_location(start_date, end_date))

@app.route("/fetch-text-from-label", methods=["GET"])
def view_feed_data():
    start_date = request.args.get("start_date", default=None)
    end_date = request.args.get("end_date", default=None)
    disaster_type = request.args.get("disaster_type")
    if disaster_type is None:
        return jsonify({"error": "disaster_type parameter is required"}), 400
    if disaster_type not in ["flood", "wildfire", "earthquake", "hurricane", "tornado"]:
        return jsonify({"error": "disaster_type parameter must be one of the following: flood, wildfire, earthquake, hurricane, tornado"}), 400
    return Response(
        json.dumps(process.fetch_text(disaster_type, start_date, end_date), ensure_ascii=False, indent=4),
        mimetype='application/json'
    )
    
@app.route("/fetch-coordinates-by-label", methods=["GET"])
def fetch_coordinates():
    start_date = request.args.get("start_date", default=None)
    end_date = request.args.get("end_date", default=None)
    disaster_type = request.args.get("disaster_type")
    if disaster_type is None:
        return jsonify({"error": "disaster_type parameter is required"}), 400

    return jsonify(process.fetch_location_coordinates(disaster_type, start_date, end_date))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)