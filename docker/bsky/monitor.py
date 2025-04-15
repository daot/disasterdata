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
import joblib
import redis
import pandas as pd
from geocode_redis import fetch_geocode
from datetime import datetime, timedelta, timezone
from atproto import AsyncClient
from pprint import pprint
from urllib.parse import urljoin
from atproto_client import exceptions
from dotenv import load_dotenv
from preprocess import bsk_preprocessor_sw, locations
from nlp_loader import get_nlp, get_p
from sklearn.preprocessing import LabelEncoder
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

### GLOBAL VARS ###

load_dotenv()
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_model"))
NLP = get_nlp()
P = get_p()
REQUEST_LIMIT = int(os.environ.get("REQUEST_LIMIT", "3000"))
TIME_WINDOW = int(os.environ.get("TIME_WINDOW", "300"))
API_TIMEOUT = float(os.environ.get("API_TIMEOUT", TIME_WINDOW / REQUEST_LIMIT / 1000))
model, label_encoder = joblib.load("data_model/models/lgbm_model_encoder_v1.pkl")
analyzer = SentimentIntensityAnalyzer() # Initialize the vader sentiment analyzer

### NEW CHANGE: Redis connection and Global Variables ###
### Maximum of 5 requests per second ###
MAX_RPS = 5  
semaphore = asyncio.Semaphore(MAX_RPS)
redis_host = os.getenv('REDIS_HOST', 'redis')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_cli = redis.Redis(host=redis_host, port=redis_port, db=1, decode_responses=True)
API_KEY = os.getenv('API_KEY')
GEOCODE_URL = os.getenv('GEOCODE_URL') #Using HERE API

logger = logging.getLogger(__name__)


### Extracts locations and returns the first one as a string ###
### Ideally do this before cleaning the text since we might want capitalization ###
### If there are no locations or error, returns empty string
def get_location(text):
    if not text or text.strip() == "":
        logger.error("Skipping empty post during location extraction.")
        return None
    try:
        loc = locations(text, NLP)  # Changed to only return one location
        if loc:
            return loc
        else:
            return None
    except Exception as e:
        logger.error("Error getting locations: %s", e)
        return None


### Applies the same preprocessing that was used for model training ###
### Returns the cleaned text as a string ###
def clean_post(text):
    if not text or text.strip() == "":
        logger.error("Skipping empty post during text cleaning.")
        return None
    try:
        cleaned_text = bsk_preprocessor_sw(text, NLP, P)
        return cleaned_text
    except Exception as e:
        logger.error("Error cleaning text: %s", e)
        return None


### Applies our model and returns the value of its prediction ###
### The default label is "other" in case of failure ###
def predict_post(cleaned_text):
    if (
        not cleaned_text or cleaned_text.strip() == ""
    ):  # Ensure text is not empty or just spaces
        logger.error("Skipping empty post during classification.")
        return "other"
    cleaned_text = [cleaned_text]  # Convert to a list of str
    try:
        prediction = model.predict(cleaned_text)
        prediction_text = label_encoder.inverse_transform(prediction)
        return str(prediction_text[0])
    except Exception as e:
        logger.error("Error applying model: %s", e)
        return "other"  # Default label in case of failure


def save_post(
    post_id, author, handle, timestamp, query, text, cleaned, label, location, sentiment, norm_loc, lat, lng
):
    """Saves a post into the database if it does not already exist."""
    session = requests.Session()
    session.trust_env = False
    response = session.post(
        f"{urllib.parse.urljoin(os.environ['DB_HOST'], 'add_row')}",
        data={
            "id": post_id,
            "timestamp": timestamp,
            "query": query,
            "author": author,
            "handle": handle,
            "text": text,
            "cleaned": cleaned,
            "label": label,
            "location": location,
            "sentiment": sentiment,
            ### New fields ###
            "norm_loc": norm_loc,
            "lat": lat,
            "lng": lng,
        },
    )
    try:
        j_response = json.loads(response.text)
    except json.decoder.JSONDecodeError as e:
        logger.error(e)
        logger.error(response.text)
        logger.error(
            (
                post_id,
                author,
                handle,
                timestamp,
                query,
                text,
                cleaned,
                label,
                location,
                sentiment,
                ### New fields ###
                norm_loc,
                lat,
                lng,
            )
        )
        return
    if j_response.get("error"):
        logger.error(j_response.get("error"))


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
            except exceptions.UnauthorizedError as e:
                logger.warning("Access token expired. Attempting to refresh session...")
                try:
                    await client.refresh_session()
                    logger.info("Session refreshed successfully.")
                except Exception as refresh_error:
                    logger.error("Failed to refresh session: %s", refresh_error)
                    await asyncio.sleep(30)  # backoff before retry
            except Exception as e:
                logger.error("Error fetching posts: %s", e)
            await asyncio.sleep(API_TIMEOUT)


def analyze_sentiment(text):
    """Analyzes the sentiment of the text and returns decimal value"""
    sentiment_score = analyzer.polarity_scores(text)['compound']
    return sentiment_score

### NEW CHANGE: Function to load data into Redis from CSV 
### Pipelines converted data frame to Redis in batches
async def load_csv(filename):
    logging.info(f"Processing {filename}...")

    df = pd.read_csv(filename, usecols=["city", "lat", "lng"], sep=",")
    df = df.drop_duplicates(subset=["city"])
    logging.info(f"Loaded {len(df)} rows from {filename}.")

    pipeline = redis_cli.pipeline()

    for row in df.itertuples(index=False):
        city = row.city
        mapping = {"lat": row.lat, "lng": row.lng}
        pipeline.hset(city, mapping=mapping)
        logging.info(f"Added {city} to Redis with mapping: {mapping}")    
    pipeline.execute()
    logging.info(f"Finished processing {filename}.")

async def process_posts(session, queue):
    """Processes and saves posts from the queue."""
    while True:
        q = await queue.get()
        query = q[0]
        post = q[1]
        post_id = post.uri
        timestamp = (
            dateutil.parser.parse(post.record.created_at, fuzzy=True) 
            .astimezone(timezone.utc)  # UTC
            .isoformat()
        )
        text = post.record.text
        author = post.author.display_name
        handle = post.author.handle

        ## Implementing a minimum word count
        # SKIP posts that do not meet the minimum word count
        min_words = 8
        if len(text.split()) < min_words:
            continue

        # Get the locations
        location = get_location(text)
        if location is None: # SKIP posts that do not mention a location
            continue
        sentiment = analyze_sentiment(text)

        # Clean the text and get the prediction
        cleaned = clean_post(text)
        label = predict_post(cleaned)

        ### NEW CHANGE: Get the coordinates ###
        norm_loc, lat, lng = await fetch_geocode(session, location, semaphore, redis_cli, GEOCODE_URL, API_KEY)

        logger.info(
            "[%s] [%s: %s] %s (%s): \n%.150s%s",
            timestamp,  # UTC
            label,
            sentiment,
            author,
            handle,
            text.replace("\n", " "),
            ("..." if len(text) > 150 else ""),
        )

        # Do not store irrelevant posts
        valid_labels = ["hurricane", "flood", "tornado", "wildfire", "earthquake"]
        if label not in valid_labels:
            logger.error("Post is not relevant!!")
            continue

        save_post(
            post_id,
            author,
            handle,
            timestamp,
            query,
            text,
            cleaned,
            label,
            location,
            sentiment,
            ### New fields ###
            norm_loc,
            lat,
            lng,
        )
        queue.task_done()


async def main():
    logger.info("Starting Bluesky monitoring script.")

    try:
        queries = [q.strip() for q in os.environ["QUERIES"].split(",")]
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
        since = dateutil.parser.parse(
            os.environ.get("SINCE"), fuzzy=True
        ).strftime(  # CST
            "%Y-%m-%dT%H:%M:%SZ"
        )
        until = dateutil.parser.parse(
            os.environ.get("UNTIL"), fuzzy=True
        ).strftime(  # CST
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
        since = (datetime.now() - time_range).strftime("%Y-%m-%dT%H:%M:%SZ")  # CST
        until = ""

    ### NEW CHANGE: Load CSV files into Redis if not already loaded ###
    if redis_cli.dbsize() < 60754:
        await asyncio.gather(
            load_csv("uscities.csv"),
            load_csv("worldcities.csv")
        )
    else:
        logging.info("Redis cache already populated with uscities.csv and worldcities.csv.")

    queue = asyncio.Queue()
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            fetch_posts(client, queue, queries, since, until),
            process_posts(
                session,
                queue,
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())