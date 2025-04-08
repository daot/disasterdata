from flask import Flask, request
import pandas as pd
import psycopg2
import os
import hashlib
import logging
import sys
from dotenv import load_dotenv
from flask_cors import CORS
import dateutil.parser

load_dotenv()
app = Flask(__name__)
CORS(app)
logger = logging.getLogger(__name__)


def get_db_connection():
    return psycopg2.connect(
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
    )


def init_table():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS posts (
                    id TEXT PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    query TEXT NOT NULL,
                    author TEXT,
                    handle TEXT,
                    text TEXT NOT NULL,
                    cleaned TEXT,
                    label TEXT,
                    location TEXT,
                    sentiment TEXT
                )
                """
            )
            # Also create the locations table
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS locations (
                    norm_loc TEXT PRIMARY KEY,
                    lat REAL NOT NULL,
                    lng REAL NOT NULL
                )
                """
            )
            conn.commit()
            logger.info("Connected to DB")


@app.route("/add_row", methods=["POST"])
def add_row():
    request_data = request.form.to_dict()

    required_fields = {"id", "timestamp", "query", "handle", "text"}
    optional_fields = {"author", "cleaned", "label", "location", "sentiment"}

    if not required_fields.issubset(request_data.keys()):
        logger.error(f"Missing required fields")
        return {"error": "Missing required fields"}, 400

    values = (
        request_data.get("id"),
        request_data.get("timestamp"),
        request_data.get("query"),
        request_data.get("author"),
        request_data.get("handle"),
        request_data.get("text"),
        request_data.get("cleaned"),
        request_data.get("label"),
        request_data.get("location"),
        request_data.get("sentiment"),
    )

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO posts (id, timestamp, query, author, handle, text, cleaned, label, location, sentiment)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    values,
                )
                conn.commit()
    except psycopg2.IntegrityError:
        logger.error("Post already in db!!")
        return {"error": "Post already in db"}, 400

    logger.info(f'Row added successfully, "id": {request_data["id"]}')
    return {"message": "Row added successfully", "id": request_data["id"]}, 201


@app.route("/edit_row", methods=["POST"])
def edit_row():
    request_data = request.form.to_dict()

    row_id = request_data.pop("id")

    allowed_fields = {"cleaned", "label", "location", "sentiment"}
    if not request_data.keys() <= allowed_fields:
        logger.error("Only 'cleaned', 'label', 'location', and 'sentiment' can be updated")
        return {"error": "Only 'cleaned', 'label', 'location', and 'sentiment' can be updated"}, 400

    set_clause = ", ".join([f"{key} = %s" for key in request_data.keys()])
    values = tuple(request_data.values()) + (row_id,)

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"UPDATE posts SET {set_clause} WHERE id = %s", values)
            conn.commit()

    logger.info(f'Row updated successfully, "id": {row_id}')
    return {"message": "Row updated successfully"}, 200


@app.route("/get_latest_posts", methods=["GET"])
def get_latest_posts():
    request_data = request.args.to_dict()
    start_timestamp = request_data.get("start_timestamp", "1970-01-01T00:00:00")
    start_timestamp = dateutil.parser.parse(start_timestamp + ' UTC', fuzzy=True).strftime("%Y-%m-%dT%H:%M:%SZ")

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, timestamp, query, author, handle, text, cleaned, label, location, sentiment
                FROM posts WHERE timestamp > %s ORDER BY timestamp ASC
                """,
                (start_timestamp,),
            )
            rows = cur.fetchall()

    posts = []
    latest_timestamp = start_timestamp
    for row in rows:
        post = {
            "id": row[0],
            "timestamp": row[1],
            "query": row[2],
            "author": row[3],
            "handle": row[4],
            "text": row[5],
            "cleaned": row[6],
            "label": row[7],
            "location": row[8],
            "sentiment": row[9]
        }
        posts.append(post)
        latest_timestamp = row[1]

    logger.info(f"Post till timestamp {latest_timestamp} returned")
    return {"posts": posts, "latest_timestamp": latest_timestamp}


@app.route("/add_location", methods=["POST"])
def add_location():
    request_data = request.form.to_dict()

    required_fields = {"norm_loc", "lat", "lng"}

    if not required_fields.issubset(request_data.keys()):
        logger.error(f"Missing required fields")
        return {"error": "Missing required fields"}, 400
    
    # lat and lng to float
    try:
        lat = float(request_data.get("lat"))
        lng = float(request_data.get("lng"))
    except ValueError:
        logger.error("Invalid lat or lng value")
        return {"error": "Invalid lat or lng value"}, 400

    values = (
        request_data.get("norm_loc"),
        lat,
        lng,
    )

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO locations (norm_loc, lat, lng)
                    VALUES (%s, %s, %s)""",
                    values,
                )
                conn.commit()
    except psycopg2.IntegrityError:
        logger.error("Location already in db")
        return {"error": "Location already in db"}, 400

    logger.info(f'Row added successfully, "norm_loc": {request_data["norm_loc"]}')
    return {"message": "Row added successfully", "norm_loc": request_data["norm_loc"]}, 201

@app.route("/get_location", methods=["GET"])
def get_location():
    request_data = request.args.to_dict() # Make sure to run as /get_location?norm_loc=LocationName
    loc = request_data.get("norm_loc")

    if not loc:
        return {"error": "Missing required field 'norm_loc'"}, 400

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT lat, lng
                FROM locations 
                WHERE norm_loc = %s
                """,
                (loc),
            )
            row = cur.fetchone()
    
    # return the coordinates
    if row: 
        coordinates = {
            "lat": row[0],
            "lng": row[1]
        }

        logger.info(f"Coordinates for {loc} returned")
        return {"coordinates": coordinates}


    logger.info(f"Coordinates for {loc} not yet in database")
    return {"error": f"Location '{loc}' not found in the database."}, 404

if __name__ == "__main__":
    try:
        levels = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL,
        }
        loglevel = levels[os.environ.get("LOGLEVEL", "info").lower()]
    except KeyError:
        logger.error("Invalid log level")
        exit()
    logger.setLevel(loglevel)
    logging.basicConfig(
        level=loglevel,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(os.environ.get("LOG", "db.log"), encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    init_table()
    app.run(host="0.0.0.0", port=5001)
