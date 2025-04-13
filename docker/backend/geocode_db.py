
"""Geocoding script to check database for locations and geocode if not found."""
import pandas as pd
import redis
import csv
import logging
import os
import asyncio
import re
import requests
import aiohttp
import us
from dotenv import load_dotenv
from urllib.parse import urlparse

#Load environment variables
load_dotenv()

#env vars
API_URL = os.getenv('API_URL')  #posts url
API_KEY = os.getenv('API_KEY')
GEOCODE_URL = os.getenv('GEOCODE_URL')  #Using HERE API
MAX_RPS = 5  #Maximum of 5 requests per second

ABBREVIATIONS = {
    "la": "Los Angeles",
    "nyc": "New York City",
    "sf": "San Francisco",
    "us": "United States",
    "usa": "United States",
    "uk": "United Kingdom",
    "dc": "Washington, D.C.",
    "on": "Ontario",
    "ca": "Canada",
    "cali": "California",
    "kc": "Kansas City",
    "kcmo": "Kansas City"
}

# Setup logging
"""logging.basicConfig(
    filename="geocode_debug.log",
    level=logging.DEBUG,
    filemode="w",
    format="%(asctime)s %(message)s"
)"""

# Redis connection
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


def fetch_data():
    response = requests.get(API_URL+"/get_latest_posts")
    if response.status_code != 200:
        return pd.DataFrame()
    data = response.json()
    posts = data.get("posts", [])
    return pd.DataFrame(posts)

async def check_db(norm_loc, session):
    #Check if location is in the db
    try:
        async with session.get(f'{API_URL}/get_location?norm_loc={norm_loc}') as response:
            if response.status == 200:
                logging.info(f"Location {norm_loc} found in the database.")
                return await response.json()  # Return coordinates (lat, lng)
            elif response.status == 404:
                logging.info(f"Location {norm_loc} not found in the database.")
                return None
    except Exception as e:
        logging.error(f"Error checking database for {norm_loc}. Status code: {response.status}")
        return None

async def save_in_db(norm_loc, lat, lng, session):
    #Save the location in the db
    data = {
        'norm_loc': norm_loc,
        'lat': lat,
        'lng': lng
    }
    try:
        async with session.post(f'{API_URL}/add_location', data=data) as response:
            if response.status == 201:
                logging.info(f"Location {norm_loc} saved to database")
            else:
                logging.error(f"Failed to save location {norm_loc} to database. Status code: {response.status}")
    except Exception as e:
        logging.error(f"Error saving location {norm_loc} to database: {e}")


def normalize_location(location):
    """Normalize location string for better matching."""
    location = location.lower()

    #Remove special characters and extra spaces
    location = re.sub(r'[^a-zA-Z0-9\s]', '', location)
    location = re.sub(r'\s+', ' ', location).strip()

    #Accounting for state abbreviations
    state = us.states.lookup(location)
    if state is not None:
        return state.name
    
    #Check for common abbreviations
    if location in ABBREVIATIONS:
        return ABBREVIATIONS[location]
    return location.title()

def is_url(string):
    try:
        # Prepend scheme if missing
        if not string.startswith(('http://', 'https://')):
            string = 'http://' + string

        result = urlparse(string)
        netloc = result.netloc.lower()

        # Valid URL if netloc contains at least one dot and isn't just www.
        return bool(netloc and '.' in netloc and netloc != 'www.')
    except Exception:
        return False

async def fetch_geocode(session, location, semaphore):

    #Skipping location if it is a URL or if it is a digit
    if is_url(location):
        logging.info(f"Skipping URL location: {location}")
        return None
        
    if location.isdigit():
        logging.info(f"Skipping numeric location: {location}")
        return None

    norm_loc = normalize_location(location)

    #Location skipped if in db
    db_data = await check_db(norm_loc, session)
    if db_data:
        logging.info(f"Cache hit: {norm_loc}")
        return db_data
    
    #Only allowing 5 concurrent tasks
    async with semaphore:
        try:
            async with session.get(GEOCODE_URL.format(location, API_KEY)) as response: 
                if response.status == 200:
                    data = await response.json()
                else:
                    logging.error(f"Failed to geocode location for {location} with Status Code: {response.status}")
                    return None
        except Exception as e:
            logging.warning(f"Error in retrieving coordinates for {location} with {e}")
            return None

    #Matching the HERE API response format
    if data.get("items"):  
        lat = data["items"][0]["position"]["lat"]
        lng = data["items"][0]["position"]["lng"]

        #Save into db
        await save_in_db(norm_loc, lat, lng, session)
        logging.info(f"{norm_loc} geocoded as ({lat}, {lng})")
        return {'norm_loc': norm_loc, 'lat': lat, 'lng': lng }
    
    logging.error(f"Failed to geocode: {location} (no results returned)")
    return None

#referenced in main function
async def geocode_locations(df):

    #respecting rate limit with semaphore
    semaphore = asyncio.Semaphore(MAX_RPS)
    try: 
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_geocode(session, location, semaphore) for location in df["location"]]
            await asyncio.gather(*tasks)
    except Exception as e:
        logging.error(f"Error in geocoding locations: {e}")

async def get_location_coordinates(location):
    semaphore = asyncio.Semaphore(MAX_RPS)
    async with aiohttp.ClientSession() as session:
        return await fetch_geocode(session, location, semaphore)


#Main function
async def main():
    logging.info("Starting program...")

    df = fetch_data()
    if not df.empty:
        logging.info(f"Fetched {len(df)} posts from API.")
    else:
        logging.info("Failed to fetch data from API.")
    df_cleaned = df[['location']].dropna().drop_duplicates()

    logging.info(f"Geocoding of {200} locations...")
    await geocode_locations(df_cleaned.head(200))

# Run the main function
if __name__ == "__main__":
    asyncio.run(main()) 
    

