import asyncio
import aiohttp
import sqlite3
import sys
import dateutil.parser
import argparse
from datetime import datetime, timedelta
from atproto import AsyncClient
from textblob import TextBlob
from argparse import (
    ArgumentDefaultsHelpFormatter,
    ArgumentParser,
    ArgumentTypeError,
    Namespace,
)


parser = ArgumentParser(
    formatter_class=ArgumentDefaultsHelpFormatter,
    add_help=False,
    description="Monitors Bluesky for a keyword.",
)
parser.add_argument(
    "-h", "--help", action="help", default=argparse.SUPPRESS, help="show help and exit"
)
parser.add_argument("-q", "--query", type=str, required=True, help="the search query")
parser.add_argument(
    "-c", "--context", type=str, required=True, help="the search query context"
)
args = parser.parse_args()

BSKY_USER = ""
BSKY_PASS = ""
KEYWORD = str(args.query).lower()
KEYWORD_CONTEXT = args.context
REQUEST_LIMIT = 3000
TIME_WINDOW = 300
DB_NAME = f'posts-{KEYWORD.replace(" ", "-")}.db'
LMSTUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions"
DEFAULT_MODEL = "qwen2.5-7b-instruct-1m"

DB = sqlite3.connect(DB_NAME)
CURSOR = DB.cursor()


def init_db():
    """Initializes the SQLite database and creates the necessary table."""
    CURSOR.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            author TEXT,
            handle TEXT,
            timestamp TEXT,
            text TEXT,
            sentiment FLOAT,
            related BOOL
        )
        """
    )
    DB.commit()


def analyze_sentiment(text):
    """Analyzes the sentiment of the text and returns decimal value"""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    return polarity


async def analyze_context(session, text, model=DEFAULT_MODEL):
    """
    Asynchronously call the LM Studio chat completion API with the provided messages.
    Returns the content of the assistant's reply.
    """
    headers = {
        "Content-Type": "application/json",
    }
    prompt = (
        f"Your task is to determine if the input text is about {KEYWORD_CONTEXT}. This topic may be broad don't be too careful",
        f"Return only yes if it is about {KEYWORD_CONTEXT}. IF IT IS NOT ABOUT {KEYWORD_CONTEXT}, return a one or two word summary about what the text is about",
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
                except (KeyError, IndexError) as e:
                    print("Unexpected OpenRouter response structure:", result)
                    return None
            else:
                text = await resp.text()
                print(f"OpenRouter API error: {resp.status} - {text}")
                return None
    except Exception as e:
        print("Error calling OpenRouter:", e)
        return None


def save_post(post_id, author, handle, timestamp, text, sentiment, related):
    """Saves a post into the database if it does not already exist."""
    try:
        CURSOR.execute(
            "INSERT INTO posts (id, author, handle, timestamp, text, sentiment, related) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (post_id, author, handle, timestamp, text, sentiment, related),
        )
        DB.commit()
    except sqlite3.IntegrityError:
        pass  # Ignore duplicate posts


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
        except Exception as e:
            print(f"Error fetching posts: {e}")
        await asyncio.sleep(interval)


async def process_posts(session, queue):
    """Processes and saves posts from the queue."""
    while True:
        post = await queue.get()
        post_id = post.uri  # Unique identifier for the post
        timestamp = dateutil.parser.parse(
            post.record.created_at, fuzzy=True
        ).isoformat()
        text = post.record.text
        author = post.author.display_name
        handle = post.author.handle

        res = CURSOR.execute(
            "SELECT EXISTS (SELECT 1 FROM posts WHERE id = (?))",
            (post_id,),
        )
        DB.commit()
        fetch = res.fetchone()[0]

        if not fetch:
            # Perform sentiment analysis on the post's text
            sentiment = analyze_sentiment(text)
            related = await analyze_context(session, text)
            related = related.lower()
            if "yes" in related or KEYWORD in related:
                print(
                    f"[{timestamp}] {author} ({handle}): "
                    + text[:50].replace("\n", " ")
                    + f"... Sentiment: {sentiment}"
                )
                related = 1
            else:
                print(
                    f"Post unrelated to keyword: [{timestamp}] {author} ({handle}): "
                    + text.replace("\n", " ")
                    + f"... Topic: {related}"
                )
                related = 0

            save_post(post_id, author, handle, timestamp, text, sentiment, related)
        queue.task_done()


async def main():
    async with aiohttp.ClientSession() as session:
        init_db()
        client = AsyncClient()
        await client.login(BSKY_USER, BSKY_PASS)
        queue = asyncio.Queue()

        await asyncio.gather(fetch_posts(client, queue), process_posts(session, queue))


if __name__ == "__main__":
    asyncio.run(main())
