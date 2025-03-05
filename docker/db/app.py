from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from datetime import datetime, timedelta
from dotenv import load_dotenv
import threading
import time
import os
import uuid
import hashlib
import MySQLdb

load_dotenv()
app = Flask(__name__)
mysql = MySQL()


def authenticate(auth_token):
    return (
        auth_token
        == hashlib.md5(
            (os.environ["MYSQL_USER"] + os.environ["MYSQL_PASSWORD"]).encode("utf-8")
        ).hexdigest()
    )


def init_table():
    # Ensure table exists
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS posts (
                id VARCHAR(200) PRIMARY KEY,
                timestamp TEXT NOT NULL,
                query TEXT NOT NULL,
                author TEXT,
                handle TEXT,
                text TEXT NOT NULL,
                cleaned TEXT,
                label TEXT,
                location TEXT
            )
        """
        )
        cur.execute("SET NAMES 'utf8'")
        mysql.connection.commit()
        cur.close()


@app.route("/add_row", methods=["POST"])
def add_row():
    auth_token = request.json.get("auth_token", {})
    if not authenticate(auth_token):
        return jsonify({"error": "Unauthorized"}), 403

    required_fields = {"id", "query", "text", "timestamp"}
    optional_fields = {"author", "handle", "cleaned", "label", "location"}

    data = request.json.get("data", {})
    if not required_fields.issubset(data.keys()):
        return jsonify({"error": "Missing required fields"}), 400

    values = {
        "id": data["id"],
        "timestamp": data["timestamp"],
        "query": data["query"],
        "author": (
            data.get("author").encode("unicode_escape").decode("utf-8")
            if data.get("author")
            else ""
        ),
        "handle": data.get("handle"),
        "text": data["text"].encode("unicode_escape").decode("utf-8"),
        "cleaned": data.get("cleaned"),
        "label": data.get("label"),
        "location": data.get("location"),
    }

    cur = mysql.connection.cursor()
    try:
        cur.execute(
            """INSERT INTO posts (id, timestamp, query, author, handle, text, cleaned, label, location)
            VALUES (%(id)s, %(timestamp)s, %(query)s, %(author)s, %(handle)s, %(text)s, %(cleaned)s, %(label)s, %(location)s)""",
            values,
        )
    except MySQLdb.IntegrityError:
        return jsonify({"error": "Post already in db"}), 400

    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "Row added successfully", "id": data["id"]}), 201


@app.route("/edit_row", methods=["PUT"])
def edit_row():
    auth_token = request.json.get("auth_token", {})
    if not authenticate(auth_token):
        return jsonify({"error": "Unauthorized"}), 403

    row_id = request.json.get("row_id")
    data = request.json.get("data", {})

    allowed_fields = {"cleaned", "label", "location"}
    if not data.keys() <= allowed_fields:
        return (
            jsonify(
                {"error": "Only 'cleaned', 'label', and 'location' can be updated"}
            ),
            400,
        )

    set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
    values = tuple(data.values()) + (row_id,)

    cur = mysql.connection.cursor()
    cur.execute(f"UPDATE posts SET {set_clause} WHERE id = %s", values)
    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "Row updated successfully"}), 200


@app.route("/get_latest_posts", methods=["GET"])
def get_latest_posts():
    auth_token = request.json.get("auth_token", {})
    if not authenticate(auth_token):
        return jsonify({"error": "Unauthorized"}), 403
        
    start_timestamp = request.json.get("start_timestamp", "1970-01-01T00:00:00")

    cur = mysql.connection.cursor()
    cur.execute(
        """
        SELECT id, timestamp, query, author, handle, text, cleaned, label, location 
        FROM posts WHERE timestamp > %s ORDER BY timestamp ASC
        """,
        (start_timestamp,),
    )
    rows = cur.fetchall()
    cur.close()

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
        }
        posts.append(post)
        latest_timestamp = row[1]  # Update latest timestamp

    return jsonify({"posts": posts, "latest_timestamp": latest_timestamp})


if __name__ == "__main__":
    app.config["MYSQL_HOST"] = os.environ["MYSQL_HOST"]
    app.config["MYSQL_PORT"] = int(os.environ["MYSQL_PORT"])
    app.config["MYSQL_USER"] = os.environ["MYSQL_USER"]
    app.config["MYSQL_PASSWORD"] = os.environ["MYSQL_PASSWORD"]
    app.config["MYSQL_DB"] = os.environ["MYSQL_DB"]
    mysql.init_app(app)
    init_table()

    app.run(host="0.0.0.0", port=5001)
