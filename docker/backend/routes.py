from flask import Flask, jsonify, request, Response
from data_processor import DataProcessor
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
process = DataProcessor()

@app.route("/fetch-label-count/", methods=["GET"])
def label_count():
    return jsonify(process.fetch_label_count())

@app.route("/fetch-most-frequent-word/", methods=["GET"])
def most_frequent():
    disaster_type = request.args.get("disaster_type")
    return jsonify(process.fetch_most_frequent(disaster_type))

@app.route("/fetch-posts-over-time/")
def posts_time():
    disaster_type = request.args.get("disaster_type")
    if not disaster_type:
        return jsonify({"error": "label must be provided"}), 400
    return jsonify(process.fetch_posts_over_time(disaster_type))

@app.route("/fetch-top-disaster-last-hour/", methods = ["GET"])
def top_disaster():
    return jsonify(process.fetch_top_disaster_last_hour())

@app.route("/fetch-text-from-label/", methods=["GET"])
def view_feed_data():
    disaster_type = request.args.get("disaster_type")
    #print(f"Received disaster type: {disaster_type}")
    if disaster_type is None:
        error_response = {"error": "disaster type must be provided"}
        #print("Returning error response:", error_response)
        return jsonify(error_response), 404
    data = process.fetch_text_last_hour(disaster_type)
    #print(f"Fetched data type: {type(data)}")
    return Response(
        json.dumps(data, ensure_ascii=False, indent=4),
        mimetype='application/json'
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)