from flask import Flask, jsonify, request, Response
from flask_apscheduler import APScheduler
<<<<<<< HEAD
from data_processor import DataProcessor1
=======
from data_processor import DataProcessor
>>>>>>> upstream/main
import json
import asyncio
from flask_cors import CORS
import logging
import sys

app = Flask(__name__)
CORS(app)
<<<<<<< HEAD

logger = logging.getLogger(__name__)
process = DataProcessor1()
scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.init_app(app)

logger = logging.getLogger(__name__)
=======
logger = logging.getLogger(__name__)
process = DataProcessor()
scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.init_app(app)

logger = logging.getLogger(__name__)
>>>>>>> upstream/main
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


@app.route("/fetch-label-count", methods=["GET"])
def label_count():
    start_date = request.args.get("start_date", default=None)
    end_date = request.args.get("end_date", default=None)
    return jsonify(process.fetch_label_count(start_date, end_date))

@app.route("/fetch-most-frequent-word", methods=["GET"])
def most_frequent():
<<<<<<< HEAD
    start_date = request.args.get("start_date", default=None)
    end_date = request.args.get("end_date", default=None)
=======
    disaster_type = request.args.get("disaster_type")
    return jsonify(process.fetch_most_frequent(disaster_type))

@app.route("/fetch-posts-over-time")
def posts_time():
>>>>>>> upstream/main
    disaster_type = request.args.get("disaster_type")
    if not disaster_type:
        return jsonify({"error": "disaster_type parameter must be provided"}), 400
    return jsonify(process.fetch_most_frequent(disaster_type, start_date, end_date))

<<<<<<< HEAD
@app.route("/fetch-posts-over-time")
def posts_time():
    start_date = request.args.get("start_date", default=None)
    end_date = request.args.get("end_date", default=None)
=======
@app.route("/fetch-top-disaster-last-day", methods = ["GET"])
def top_disaster():
    return jsonify(process.fetch_top_disaster_last_day())

@app.route("/fetch-text-from-label", methods=["GET"])
def view_feed_data():
>>>>>>> upstream/main
    disaster_type = request.args.get("disaster_type")
    if not disaster_type:
        return jsonify({"error": "disaster_type parameter must be provided"}), 400
    return jsonify(process.fetch_posts_over_time(disaster_type, start_date, end_date))

@app.route("/fetch-top-disaster-location", methods = ["GET"])
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
    return Response(
<<<<<<< HEAD
        json.dumps(process.fetch_text(disaster_type, start_date, end_date), ensure_ascii=False, indent=4),
=======
        json.dumps(process.fetch_text_last_day(disaster_type), ensure_ascii=False, indent=4),
>>>>>>> upstream/main
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
