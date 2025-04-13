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
from urllib.parse import urlparse
from dotenv import load_dotenv

#Load environment variables
load_dotenv()

#env vars
API_URL = os.getenv('API_URL')  #posts url
API_KEY = os.getenv('API_KEY')
GEOCODE_URL = os.getenv('GEOCODE_URL')  #Using HERE API
MAX_RPS = 5  #Maximum of 5 requests per second
DB_URL = os.getenv('DB_URL')  #location url

ABBREVIATIONS = {
    "la": "Los Angeles",
    "nyc": "New York City",
    "sf": "San Francisco",
    "us": "United States",
    "usa": "United States",
    "uk": "United Kingdom",
    "dc": "Washington, D.C.",
    "on": "Ontario",
    "ca": "Canada"
}

# Redis connection
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


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

def save_in_cache(norm_loc, lat, lng):
    """Save geocoded location into Redis cache."""
    r.hset(norm_loc, mapping={"lat": lat, "lng": lng})
    logging.info(f"Saved {norm_loc} into Redis with coordinates: ({lat}, {lng})")

def check_cache(norm_loc):
    #Check if location is in Redis cache
    if r.exists(norm_loc):
        coordinates = r.hgetall(norm_loc)
        logging.info(f"Cache hit for {norm_loc}: {coordinates} found in Redis")
        return coordinates 
    return None 

#Function to load data into Redis from CSV
async def load_csv(filename):
    logging.info(f"Processing {filename}...")

    #Convert csv file into dataframe
    df = pd.read_csv(filename, usecols=["city", "lat", "lng"], sep=",")
    df = df.drop_duplicates(subset=["city"])
    logging.info(f"Loaded {len(df)} rows from {filename}.")

    #Using pipeline for batch processing
    pipeline = r.pipeline()

    for index, row in df.iterrows():
        city = row["city"]
        mapping = {"lat": row["lat"], "lng": row["lng"]}
        pipeline.hset(city, mapping=mapping)
        logging.info(f"Added {city} to Redis with mapping: {mapping}")    
    pipeline.execute()
    logging.info(f"Finished processing {filename}.")

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
        return None

    #Location skipped if in cache
    norm_loc = normalize_location(location)
    cache_data = check_cache(norm_loc)
    if cache_data:  
        #logging.info(f"Cache hit: {norm_loc}")
        return cache_data
    
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

        #Save into cache
        save_in_cache(norm_loc, lat, lng) 

        logging.info(f"{norm_loc} geocoded as ({lat}, {lng})")
        return {'norm_loc': norm_loc, 'lat': lat, 'lng': lng }
    
    logging.error(f"Failed to geocode: {location} (no results returned)")
    return None

async def get_coordinates(location):
    logging.info(f"Redis size: {r.dbsize()}")
    if (r.dbsize() < 60754):
        await asyncio.gather(
        load_csv("uscities.csv"),
        load_csv("worldcities.csv")
        )
    else:
        logging.info("Redis cache already populated with uscities.csv and worldcities.csv.")
        
    semaphore = asyncio.Semaphore(MAX_RPS)
    async with aiohttp.ClientSession() as session:
        result = await fetch_geocode(session, location, semaphore)
        if result:
            return result['norm_loc'], result['lat'], result['lng']
        return None
