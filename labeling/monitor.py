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
# API_TIMEOUT = TIME_WINDOW / REQUEST_LIMIT / 1000
API_TIMEOUT = 1
logger = logging.getLogger(__name__)


def setup_parser():
    """Reads user options from command line arguments."""
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        add_help=False,
        description="Monitors Bluesky for a keyword.",
    )
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="show help and exit",
    )
    parser.add_argument(
        "-q", "--query", type=str, required=True, help="the search query"
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
            text TEXT,
            sentiment FLOAT,
            relevant BOOL
        )
        """
    )
    db.commit()
    logger.info("Database initialized successfully.")
    return db, cursor


def analyze_sentiment(text):
    """Analyzes the sentiment of the text and returns decimal value."""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    return polarity


async def analyze_context(session, url, text, keyword, keyword_context, model):
    """Asynchronously call the LM Studio chat completion API with the provided messages."""
    headers = {"Content-Type": "application/json"}
    messages = [
        {
            "role": "system",
            "content": " ".join(
                (
                    f"You are an AI assistant that is tasked with determining if the word {keyword} in a body of text is about {keyword_context}.",
                    f"The text is related if it is about {keyword_context} in any way.",
                    f"Return only 'yes' if the text is about {keyword_context}.",
                    f"Return only 'no' if the text is not about {keyword_context}.",
                )
            ),
        },
        {"role": "user", "content": f"{text}"},
    ]
    payload = {"model": model, "messages": messages}

    llm_res = ""
    try:
        async with session.post(url, headers=headers, json=payload) as resp:
            if resp.status == 200:
                result = await resp.json()
                try:
                    llm_res = result["choices"][0]["message"]["content"].replace(
                        "\n", " "
                    )
                    if "yes" in llm_res or keyword in llm_res:
                        return llm_res
                except (KeyError, IndexError):
                    logger.error("Unexpected LM Studio response structure: %s", result)
                    return None
            else:
                text = await resp.text()
                logger.error("LM Studio API error: %s - %s", resp.status, text)
                return None
    except Exception as e:
        logger.error("Error calling LM Studio: %s", e)
        return None

    messages = [
        {
            "role": "system",
            "content": "You are an AI assistant that is tasked with writing a one to two word description of what the input text is saying",
        },
        {"role": "user", "content": f"{text}"},
    ]
    payload = {"model": model, "messages": messages}

    llm_res2 = ""
    try:
        async with session.post(url, headers=headers, json=payload) as resp:
            if resp.status == 200:
                result = await resp.json()
                try:
                    llm_res2 = result["choices"][0]["message"]["content"].replace(
                        "\n", " "
                    )
                except (KeyError, IndexError):
                    logger.error("Unexpected LM Studio response structure: %s", result)
                    return None
            else:
                text = await resp.text()
                logger.error("LM Studio API error: %s - %s", resp.status, text)
                return None
    except Exception as e:
        logger.error("Error calling LM Studio: %s", e)
        return None

    messages = [
        {
            "role": "system",
            "content": "You are a helpful and precise research assistant.",
        },
        {
            "role": "user",
            "content": " ".join(
                (
                    f"You are an AI assistant that is tasked with determining if the word {keyword} is related to {llm_res2}.",
                    f"The text is related if it is about {keyword_context} in any way.",
                    f"Return only 'yes' if the text is about {keyword_context}.",
                    f"Return only 'no' if the text is not about {keyword_context}.",
                )
            ),
        },
    ]
    payload = {"model": model, "messages": messages}

    llm_res3 = ""
    try:
        async with session.post(url, headers=headers, json=payload) as resp:
            if resp.status == 200:
                result = await resp.json()
                try:
                    llm_res3 = result["choices"][0]["message"]["content"].replace(
                        "\n", " "
                    )
                    if "yes" in llm_res3 or keyword in llm_res3:
                        return llm_res3
                    return llm_res2
                except (KeyError, IndexError):
                    logger.error("Unexpected LM Studio response structure: %s", result)
                    return None
            else:
                text = await resp.text()
                logger.error("LM Studio API error: %s - %s", resp.status, text)
                return None
    except Exception as e:
        logger.error("Error calling LM Studio: %s", e)
        return None


def save_post(
    db, cursor, post_id, author, handle, timestamp, text, sentiment, relevant
):
    """Saves a post into the database if it does not already exist."""
    try:
        cursor.execute(
            "INSERT INTO posts (id, author, handle, timestamp, text, sentiment, relevant) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (post_id, author, handle, timestamp, text, sentiment, relevant),
        )
        db.commit()
        logger.debug(
            "Saved post from %s to db",
            post_id,
        )
    except sqlite3.IntegrityError:
        logger.info("Duplicate post ignored: %s", post_id)
        pass


async def fetch_posts(client, queue, keyword, time_delta):
    """Fetches posts continuously and adds them to the queue."""
    cursor = None
    while True:
        try:
            response = await client.app.bsky.feed.search_posts(
                {
                    "q": keyword,
                    "sort": "latest",
                    "since": (datetime.utcnow() - timedelta(**time_delta)).strftime(
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
                logger.debug("Fetched %d posts.", len(response.posts))
        except exceptions.ModelError as e:
            logger.debug("Mysterious aspect ratio error: %s", e)
        except Exception as e:
            logger.error("Error fetching posts: %s", e)
        await asyncio.sleep(API_TIMEOUT)


async def process_posts(
    db, cursor, session, queue, keyword, keyword_context, lmstudio_url, model
):
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

        if not cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM posts WHERE id = (?))", (post_id,)
        ).fetchone()[0]:
            sentiment = analyze_sentiment(text)
            relevant_text = (
                await analyze_context(
                    session, lmstudio_url, text, keyword, keyword_context, model
                )
            ).lower()
            relevant = 1 if "yes" in relevant_text or keyword in relevant_text else 0
            logger.info(
                "[%s]%s[%sRelevant, %s: %s] %s (%s): \n%.150s%s",
                timestamp,
                "+" if relevant else "-",
                "" if relevant else "Not ",
                "Sentiment" if relevant else "Topic",
                sentiment if relevant else relevant_text,
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
                text,
                sentiment,
                relevant,
            )
        queue.task_done()


async def main():
    logger.info("Starting Bluesky monitoring script.")

    args = setup_parser()
    config = load_config(args.config)

    keyword = str(args.query).lower()
    keyword_context = keyword if args.context == "The value of QUERY" else args.context

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
        f'posts-{keyword.replace(" ", "-")}.db'
        if args.db == "posts-QUERY.db"
        else args.db
    )
    db, cursor = init_db(db_name)

    host = config.get("host", "http://127.0.0.1:1234")
    lmstudio_url = (host[:-1] if host[-1] == "/" else host) + "/v1/chat/completions"

    client = AsyncClient()
    try:
        await client.login(config.get("user", ""), config.get("pass", ""))
    except ValueError:
        logger.error("Username or password is incorrect")
        exit()

    queue = asyncio.Queue()
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            fetch_posts(
                client,
                queue,
                keyword,
                time_delta={args.range.split("=")[0]: float(args.range.split("=")[1])},
            ),
            process_posts(
                db,
                cursor,
                session,
                queue,
                keyword,
                keyword_context,
                lmstudio_url,
                model=config.get("model", "maziyarpanahi/qwen2.5-7b-instruct"),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
