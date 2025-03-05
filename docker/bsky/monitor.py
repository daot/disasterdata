import asyncio
import aiohttp
import requests
import sys
import dateutil.parser
import logging
import os
import json
import hashlib
import urllib.parse
from datetime import datetime, timedelta
from atproto import AsyncClient
from textblob import TextBlob
from pprint import pprint
from urllib.parse import urljoin
from atproto_client import exceptions
from dotenv import load_dotenv

### GLOBAL VARS ###

load_dotenv()
REQUEST_LIMIT = int(os.environ.get("REQUEST_LIMIT", "3000"))
TIME_WINDOW = int(os.environ.get("TIME_WINDOW", "300"))
API_TIMEOUT = float(os.environ.get("API_TIMEOUT", TIME_WINDOW / REQUEST_LIMIT / 1000))
logger = logging.getLogger(__name__)


def save_post(post_id, author, handle, timestamp, query, text):
    """Saves a post into the database if it does not already exist."""
    session = requests.Session()
    session.trust_env = False
    response = session.post(
        f"{urllib.parse.urljoin(os.environ['DB_HOST'], 'add_row')}",
        data={
            "auth_token": hashlib.md5(
                (os.environ["DB_USER"] + os.environ["DB_PASSWORD"]).encode("utf-8")
            ).hexdigest(),
            "id": post_id,
            "timestamp": timestamp,
            "query": query,
            "author": author,
            "handle": handle,
            "text": text,
        },
    )
    try:
        j_response = json.loads(response.text)
    except json.decoder.JSONDecodeError as e:
        logger.error(e)
        logger.error((post_id, author, handle, timestamp, query, text))
        exit()
    if j_response.get("error"):
        logger.info(j_response.get("error"))


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


async def process_posts(session, queue, model):
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

        logger.info(
            "[%s] %s (%s): \n%.150s%s",
            timestamp,
            author,
            handle,
            text.replace("\n", " "),
            ("..." if len(text) > 150 else ""),
        )
        save_post(
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

    try:
        queries = os.environ["QUERIES"].split(",")
    except KeyError:
        logger.error("Missing queries")
        exit()

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
            logging.FileHandler(os.environ.get("LOG", "bsky.log"), encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

    client = AsyncClient()
    try:
        await client.login(os.environ["BSKY_USER"], os.environ["BSKY_PASS"])
    except ValueError:
        logger.error("Username or password is incorrect")
        exit()
    except KeyError:
        logger.error("Missing username or password")
        exit()

    if (os.environ.get("SINCE") and not os.environ.get("UNTIL")) or (
        os.environ.get("UNTIL") and not os.environ.get("SINCE")
    ):
        logger.error("Needs both since and until flag")
        exit()

    if os.environ.get("SINCE") or os.environ.get("UNTIL"):
        since = dateutil.parser.parse(os.environ.get("SINCE"), fuzzy=True).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        until = dateutil.parser.parse(os.environ.get("UNTIL"), fuzzy=True).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
    else:
        time_range = timedelta(
            **{
                os.environ.get("RANGE", "hours=1").split("=")[0]: float(
                    os.environ.get("RANGE", "hours=1").split("=")[1]
                )
            }
        )
        since = (datetime.utcnow() - time_range).strftime("%Y-%m-%dT%H:%M:%SZ")
        until = ""
    model = os.environ.get("MODEL", "maziyarpanahi/qwen2.5-7b-instruct")

    queue = asyncio.Queue()
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            fetch_posts(client, queue, queries, since, until),
            process_posts(
                session,
                queue,
                model,
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
