import joblib
import asyncio
import aiohttp
import sqlite3
import sys
import dateutil.parser
import argparse
import logging
import yaml
import os
from datetime import datetime, timedelta
from atproto import AsyncClient
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from atproto_client import exceptions

'''
Modified version of Henry's code -- this time just applying our prediction and seeing what it thinks.
Make sure to have config.yaml ready to go with user and password for Bluesky
'''

### GLOBAL VARS ###
REQUEST_LIMIT = 3000
TIME_WINDOW = 300
API_TIMEOUT = 1
logger = logging.getLogger(__name__)

# Load the model
demo_model = joblib.load('disaster_classification_model.pkl')


def setup_parser():
    """Reads user options from command line arguments."""
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        add_help=False,
        description="Monitors Bluesky for a query.",
    )
    parser.add_argument("-q", "--query", type=str, required=True, nargs="+", help="the search query")
    parser.add_argument("-l", "--log", type=str, default="classify.log", help="log file")
    parser.add_argument("-ll", "--loglevel", type=str, default="info", help="log level")
    parser.add_argument("-c", "--config", type=str, default="config.yaml", help="config file")
    parser.add_argument("-d", "--db", type=str, default="posts-QUERY.db", help="db location")
    parser.add_argument("-r", "--range", type=str, default="hours=1", help="date/time range for scraper")
    parser.add_argument("-s", "--since", type=str, help="start date for scraping range")
    parser.add_argument("-u", "--until", type=str, help="end date for scraping range")
    return parser.parse_args()


def load_config(config_file):
    """Reads user options in config file."""
    if not os.path.exists(config_file):
        logger.error("No config file found")
        exit()
    with open(config_file, "r") as file:
        return yaml.safe_load(file)


def init_db(db_name):
    """Initializes the SQLite database and creates the necessary table."""
    logger.info("Initializing database.")
    db = sqlite3.connect(db_name)
    cursor = db.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            author TEXT,
            handle TEXT,
            timestamp TEXT,
            query TEXT,
            text TEXT,
            label TEXT
        )
        """
    )
    db.commit()
    logger.info("Database initialized successfully.")
    return db, cursor

def apply_model(text):
    """Applies our model and returns the value of its prediction"""
    if not text or text.strip() == "":  # Ensure text is not empty or just spaces
        logger.warning("Skipping empty post during classification.")
        return "Unknown"  # Or another default label
    
    text = [text]  # Convert to a list of str
    try:
        prediction = demo_model.predict(text)
        return prediction[0]
    except Exception as e:
        logger.error("Error applying model: %s", e)
        return "Error"  # Default label in case of failure


def save_post(db, cursor, post_id, author, handle, timestamp, query, text, label):
    """Saves a post into the database if it does not already exist."""
    try:
        cursor.execute(
            "INSERT INTO posts (id, author, handle, timestamp, query, text, label) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (post_id, author, handle, timestamp, query, text, label),
        )
        db.commit()
        logger.debug("Saved post from %s to db", post_id)
    except sqlite3.IntegrityError:
        logger.info("Duplicate post ignored: %s", post_id)


async def fetch_posts(client, queue, queries, since, until):
    """Fetches posts continuously and adds them to the queue."""
    cursor = {query: "" for query in queries}
    while True:
        for query in queries:
            try:
                response = await client.app.bsky.feed.search_posts(
                    {
                        "q": query,
                        "sort": "latest",
                        "since": since,
                        "until": until,
                        "cursor": cursor[query],
                    },
                    headers={"Accept-Language": "en"},
                )
                if response.posts:
                    for post in response.posts:
                        await queue.put([query, post])
                    cursor[query] = response.cursor if hasattr(response, "cursor") else None
                    logger.debug("Fetched %d posts.", len(response.posts))
            except exceptions.ModelError as e:
                logger.debug("API error: %s", e)
            except Exception as e:
                logger.error("Error fetching posts: %s", e)
            await asyncio.sleep(API_TIMEOUT)


async def process_posts(db, cursor, queue):
    """Processes and saves posts from the queue."""
    while True:
        q = await queue.get()
        query = q[0]
        post = q[1]
        post_id = post.uri
        timestamp = dateutil.parser.parse(post.record.created_at, fuzzy=True).isoformat()
        text = post.record.text
        author = post.author.display_name
        handle = post.author.handle

        if not cursor.execute("SELECT EXISTS (SELECT 1 FROM posts WHERE id = (?))", (post_id,)).fetchone()[0]:
            label = apply_model(text)
            logger.info(
                "[%s] [%s] %s (%s): %.150s%s", 
                timestamp, 
                label, 
                author, 
                handle, 
                text.replace("\n", " "), "..." 
                if len(text) > 150 
                else ""
            )
            save_post(db, cursor, post_id, author, handle, timestamp, query, text, label)

        queue.task_done()


async def main():
    logger.info("Starting Bluesky monitoring script.")

    args = setup_parser()
    config = load_config(args.config)

    queries = args.query

    try:
        levels = {"debug": logging.DEBUG, "info": logging.INFO, "warning": logging.WARNING, "error": logging.ERROR, "critical": logging.CRITICAL}
        loglevel = levels[args.loglevel.lower()]
    except KeyError:
        logger.error("Invalid log level")
        exit()

    logger.setLevel(loglevel)
    logging.basicConfig(
        level=loglevel,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(args.log, encoding="utf-8"), logging.StreamHandler(sys.stdout)],
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

    db_name = f'posts-{"-".join(queries).replace(" ", "-")}.db' if args.db == "posts-QUERY.db" else args.db
    db, cursor = init_db(db_name)

    client = AsyncClient()
    try:
        await client.login(config.get("user", ""), config.get("pass", ""))
    except ValueError:
        logger.error("Username or password is incorrect")
        exit()

    if args.since or args.until:
        since = dateutil.parser.parse(args.since, fuzzy=True).strftime("%Y-%m-%dT%H:%M:%SZ")
        until = dateutil.parser.parse(args.until, fuzzy=True).strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        time_range = timedelta(**{args.range.split("=")[0]: float(args.range.split("=")[1])})
        since = (datetime.utcnow() - time_range).strftime("%Y-%m-%dT%H:%M:%SZ")
        until = ""

    queue = asyncio.Queue()
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            fetch_posts(client, queue, queries, since, until),
            process_posts(db, cursor, queue),
        )


if __name__ == "__main__":
    asyncio.run(main())