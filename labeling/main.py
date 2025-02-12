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
from textblob import TextBlob
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from pprint import pprint
from urllib.parse import urljoin
from atproto_client import exceptions

### GLOBAL VARS ###

REQUEST_LIMIT = 3000
TIME_WINDOW = 300

### PARSER SETUP ###

parser = ArgumentParser(
    formatter_class=ArgumentDefaultsHelpFormatter,
    add_help=False,
    description="Monitors Bluesky for a keyword.",
)
parser.add_argument(
    "-h", "--help", action="help", default=argparse.SUPPRESS, help="show help and exit"
)
parser.add_argument("-q", "--query", type=str, required=True, help="the search query")
TVOQ = "The value of QUERY"
parser.add_argument(
    "-x",
    "--context",
    type=str,
    default=TVOQ,
    help="additional query context to help the LLM",
)
parser.add_argument(
    "-l",
    "--log",
    type=str,
    default="runtime.log",
    help="log file",
)
parser.add_argument(
    "-ll",
    "--loglevel",
    type=str,
    default="info",
    help="log level (debug, info, warning, error, critical)",
)
parser.add_argument(
    "-c",
    "--config",
    type=str,
    default="config.yaml",
    help="config file",
)
args = parser.parse_args()

### ARGUMENT-BASED GLOBAL VARIABLES ###

KEYWORD = str(args.query).lower()
KEYWORD_CONTEXT = KEYWORD if args.context == TVOQ else args.context
DB_NAME = f'posts-{KEYWORD.replace(" ", "-")}.db'
try:
    LEVELS = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    LOGLEVEL = LEVELS[args.loglevel.lower()]
except KeyError:
    logging.error("Invalid log level")
    exit()
LOG_FILE = args.log

### READ CONFIG VALUES ###

if not os.path.exists(args.config):
    logging.error("No config file found")
    create = input(f"Create {args.config} y/n: ").lower()
    if create == "y":
        with open(args.config, "w") as file:
            file.write("user:\npass:")
    exit()
with open(args.config, "r") as file:
    config = yaml.safe_load(file)

BSKY_USER = config.get("user", "")
BSKY_PASS = config.get("pass", "")
LMSTUDIO_URL = config.get("host", "http://127.0.0.1:1234") + "/v1/chat/completions"
MODEL_NAME = config.get("model", "qwen2.5-7b-instruct-1m")

### LOGGING SETUP ###

logging.getLogger().setLevel(LOGLEVEL)
logging.basicConfig(
    level=LOGLEVEL,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logging.getLogger("httpx").setLevel(logging.WARNING)

### DB SETUP ###

DB = sqlite3.connect(DB_NAME)
CURSOR = DB.cursor()


def init_db():
    """Initializes the SQLite database and creates the necessary table."""
    logging.info("Initializing database.")
    CURSOR.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            author TEXT,
            handle TEXT,
            timestamp TEXT,
            text TEXT,
            sentiment FLOAT,
            relevant BOOL
        )
        """
    )
    DB.commit()
    logging.info("Database initialized successfully.")


def analyze_sentiment(text):
    """Analyzes the sentiment of the text and returns decimal value."""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    return polarity


async def analyze_context(session, text, model=MODEL_NAME):
    """Asynchronously call the LM Studio chat completion API with the provided messages."""
    headers = {"Content-Type": "application/json"}
    prompt = (
        f"Your task is to determine if the input text is about {KEYWORD_CONTEXT}. Be as generous as possible in interpreting the context.",
        f"Return only 'yes' if the text is about {KEYWORD_CONTEXT}.",
        f"If the text is not about {KEYWORD_CONTEXT}, return a one to two-word summary of its topic.",
    )
    messages = [
        {
            "role": "system",
            "content": "You are a helpful and precise research assistant.",
        },
        {"role": "user", "content": f"Input text: {text}\n\n{prompt}"},
    ]
    payload = {"model": model, "messages": messages}

    try:
        async with session.post(LMSTUDIO_URL, headers=headers, json=payload) as resp:
            if resp.status == 200:
                result = await resp.json()
                try:
                    return result["choices"][0]["message"]["content"].replace("\n", " ")
                except (KeyError, IndexError):
                    logging.error("Unexpected LM Studio response structure: %s", result)
                    return None
            else:
                text = await resp.text()
                logging.error("LM Studio API error: %s - %s", resp.status, text)
                return None
    except Exception as e:
        logging.error("Error calling LM Studio: %s", e)
        return None


def save_post(post_id, author, handle, timestamp, text, sentiment, relevant):
    """Saves a post into the database if it does not already exist."""
    try:
        CURSOR.execute(
            "INSERT INTO posts (id, author, handle, timestamp, text, sentiment, relevant) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (post_id, author, handle, timestamp, text, sentiment, relevant),
        )
        DB.commit()
        logging.debug(
            "Saved post from %s to db",
            post_id,
        )
    except sqlite3.IntegrityError:
        logging.info("Duplicate post ignored: %s", post_id)
        pass


async def fetch_posts(client, queue):
    """Fetches posts continuously and adds them to the queue."""
    cursor = None
    interval = TIME_WINDOW / REQUEST_LIMIT
    while True:
        try:
            response = await client.app.bsky.feed.search_posts(
                {
                    "q": KEYWORD,
                    "sort": "latest",
                    "since": (datetime.utcnow() - timedelta(hours=1)).strftime(
                        "%Y-%m-%dT%H:%M:%SZ"
                    ),
                    "cursor": cursor,
                },
                headers={"Accept-Language": "en"},
            )
            if response.posts:
                for post in response.posts:
                    await queue.put(post)
                cursor = response.cursor if hasattr(response, "cursor") else None
                logging.debug("Fetched %d posts.", len(response.posts))
        except exceptions.ModelError as e:
            logging.debug("Mysterious aspect ratio error: %s", e)
        except Exception as e:
            logging.error("Error fetching posts: %s", e)
        await asyncio.sleep(interval)


async def process_posts(session, queue):
    """Processes and saves posts from the queue."""
    while True:
        post = await queue.get()
        post_id = post.uri
        timestamp = dateutil.parser.parse(
            post.record.created_at, fuzzy=True
        ).isoformat()
        text = post.record.text
        author = post.author.display_name
        handle = post.author.handle

        res = CURSOR.execute(
            "SELECT EXISTS (SELECT 1 FROM posts WHERE id = (?))", (post_id,)
        )
        DB.commit()
        fetch = res.fetchone()[0]

        if not fetch:
            sentiment = analyze_sentiment(text)
            relevant = await analyze_context(session, text)
            relevant = relevant.lower()
            if "yes" in relevant or KEYWORD in relevant:
                logging.info(
                    "[%s] %s (%s): %.50s... [Relevant, Sentiment: %f]",
                    timestamp,
                    author,
                    handle,
                    text.replace("\n", " "),
                    sentiment,
                )
                relevant = 1
            else:
                logging.info(
                    "[%s] %s (%s): %.50s... [Not relevant, Topic: %s]",
                    timestamp,
                    author,
                    handle,
                    text.replace("\n", " "),
                    relevant,
                )
                relevant = 0
            save_post(post_id, author, handle, timestamp, text, sentiment, relevant)
        queue.task_done()


async def main():
    logging.info("Starting Bluesky monitoring script.")
    async with aiohttp.ClientSession() as session:
        init_db()
        client = AsyncClient()
        try:
            await client.login(BSKY_USER, BSKY_PASS)
        except ValueError:
            logging.error("Username or password is incorrect")
            exit()
        queue = asyncio.Queue()
        await asyncio.gather(fetch_posts(client, queue), process_posts(session, queue))


if __name__ == "__main__":
    asyncio.run(main())
