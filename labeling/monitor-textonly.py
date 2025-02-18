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
from pprint import pprint
from urllib.parse import urljoin
from atproto_client import exceptions

### GLOBAL VARS ###

REQUEST_LIMIT = 3000
TIME_WINDOW = 300
# API_TIMEOUT = TIME_WINDOW / REQUEST_LIMIT / 1000
API_TIMEOUT = 1
logger = logging.getLogger(__name__)


def setup_parser():
    """Reads user options from command line arguments."""
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        add_help=False,
        description="Monitors Bluesky for a query.",
    )
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="show help and exit",
    )
    parser.add_argument(
        "-q",
        "--query",
        type=str,
        required=True,
        action="extend",
        nargs="+",
        help="the search query",
    )
    parser.add_argument(
        "-x",
        "--context",
        type=str,
        default="The value of QUERY",
        help="additional query context to help the LLM",
    )
    parser.add_argument(
        "-l",
        "--log",
        type=str,
        default="monitor-textonly.log",
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
    parser.add_argument(
        "-d",
        "--db",
        type=str,
        default="posts-QUERY.db",
        help="db location",
    )
    parser.add_argument(
        "-r",
        "--range",
        type=str,
        default="hours=1",
        help="date/time range for scraper (days, seconds, microseconds, milliseconds, minutes, hours, weeks)",
    )
    parser.add_argument(
        "-s",
        "--since",
        type=str,
        help="start date for scraping range",
    )
    parser.add_argument(
        "-u",
        "--until",
        type=str,
        help="end date for scraping range",
    )
    return parser.parse_args()


def load_config(config_file):
    """Reads user options in config file."""
    if not os.path.exists(config_file):
        logger.error("No config file found")
        create = input(f"Create {config_file} y/n: ").lower()
        if create == "y":
            with open(config_file, "w") as file:
                file.write("user:\npass:")
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
            text TEXT
        )
        """
    )
    db.commit()
    logger.info("Database initialized successfully.")
    return db, cursor


def save_post(db, cursor, post_id, author, handle, timestamp, query, text):
    """Saves a post into the database if it does not already exist."""
    try:
        cursor.execute(
            "INSERT INTO posts (id, author, handle, timestamp, query, text) VALUES (?, ?, ?, ?, ?, ?)",
            (post_id, author, handle, timestamp, query, text),
        )
        db.commit()
        logger.debug(
            "Saved post from %s to db",
            post_id,
        )
    except sqlite3.IntegrityError:
        logger.info("Duplicate post ignored: %s", post_id)
        pass


async def fetch_posts(client, queue, queries, since, until):
    """Fetches posts continuously and adds them to the queue."""
    cursor = {}
    [cursor.update({query: ""}) for query in queries]
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
                    cursor[query] = (
                        response.cursor if hasattr(response, "cursor") else None
                    )
                    logger.debug("Fetched %d posts.", len(response.posts))
            except exceptions.ModelError as e:
                logger.debug("Mysterious aspect ratio error: %s", e)
            except Exception as e:
                logger.error("Error fetching posts: %s", e)
            await asyncio.sleep(API_TIMEOUT)


async def process_posts(db, cursor, session, queue, queries_context):
    """Processes and saves posts from the queue."""
    while True:
        q = await queue.get()
        query = q[0]
        post = q[1]
        post_id = post.uri
        timestamp = dateutil.parser.parse(
            post.record.created_at, fuzzy=True
        ).isoformat()
        text = post.record.text
        author = post.author.display_name
        handle = post.author.handle

        if not cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM posts WHERE id = (?))", (post_id,)
        ).fetchone()[0]:
            logger.info(
                "[%s] %s (%s): \n%.150s%s",
                timestamp,
                author,
                handle,
                text.replace("\n", " "),
                ("..." if len(text) > 150 else ""),
            )
            save_post(
                db,
                cursor,
                post_id,
                author,
                handle,
                timestamp,
                query,
                text,
            )
        queue.task_done()


async def main():
    logger.info("Starting Bluesky monitoring script.")

    args = setup_parser()
    config = load_config(args.config)

    queries = args.query
    queries_context = (
        ", ".join(queries) if args.context == "The value of QUERY" else args.context
    )

    try:
        levels = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL,
        }
        loglevel = levels[args.loglevel.lower()]
    except KeyError:
        logger.error("Invalid log level")
        exit()
    logger.setLevel(loglevel)
    logging.basicConfig(
        level=loglevel,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(args.log, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

    db_name = (
        f'posts-{"-".join(queries).replace(" ", "-")}.db'
        if args.db == "posts-QUERY.db"
        else args.db
    )
    db, cursor = init_db(db_name)

    host = config.get("host", "http://127.0.0.1:1234")

    client = AsyncClient()
    try:
        await client.login(config.get("user", ""), config.get("pass", ""))
    except ValueError:
        logger.error("Username or password is incorrect")
        exit()

    if (args.since and not args.until) or (args.until and not args.since):
        logger.error("Needs both since and until flag")
        exit()

    if args.since or args.until:
        since = dateutil.parser.parse(args.since, fuzzy=True).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        until = dateutil.parser.parse(args.until, fuzzy=True).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
    else:
        time_range = timedelta(
            **{args.range.split("=")[0]: float(args.range.split("=")[1])}
        )
        since = (datetime.utcnow() - time_range).strftime("%Y-%m-%dT%H:%M:%SZ")
        until = ""

    queue = asyncio.Queue()
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            fetch_posts(client, queue, queries, since, until),
            process_posts(
                db,
                cursor,
                session,
                queue,
                queries_context,
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
