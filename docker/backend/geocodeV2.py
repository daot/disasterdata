import pandas as pd
import psycopg2
import redis
import csv
import logging
import os
import asyncio
import rapidfuzz
import re
import requests
import aiohttp
import us
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
    "sf": "San Francisco"
}

# Redis connection
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Setup logging
logging.basicConfig(
    filename="geocode_debug.log",
    level=logging.INFO,
    filemode="w",
    format="%(asctime)s %(message)s"
)

def fetch_data():
    response = requests.get(API_URL+"/get_latest_posts")
    if response.status_code != 200:
        return pd.DataFrame()
    data = response.json()
    posts = data.get("posts", [])
    return pd.DataFrame(posts)

async def check_db(norm_loc):
    #Check if location is in the db

    #response = requests.get(f'{DB_URL}/get_location?norm_loc={norm_loc}')
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{DB_URL}/get_location?norm_loc={norm_loc}') as response:
            if response.status == 200:
                logging.info(f"Location {norm_loc} found in the database.")
                return response.json()  # Return coordinates (lat, lng)
            elif response.status == 404:
                logging.info(f"Location {norm_loc} not found in the database.")
                return None
            else:
                logging.error(f"Error checking database for {norm_loc}. Status code: {response.status}")
            return None

async def save_in_db(norm_loc, lat, lng):
    #Save the location in the db
    data = {
        'norm_loc': norm_loc,
        'lat': lat,
        'lng': lng
    }
    #response = requests.post(f'{DB_URL}/add_location', data=data)
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f'{DB_URL}/add_location', data=data) as response:
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

async def fetch_geocode(session, location, semaphore):

    #Skipping location if it is a URL or if it is a digit
    if re.match(r'^(https?://)?(www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(/[^\s]*)?$', location):
        return None
    if location.isdigit():
        return None
        
    #Location skipped if in cache
    norm_loc = normalize_location(location)
    cache_data = check_cache(norm_loc)
    if cache_data:  
        logging.info(f"Cache hit: {norm_loc}")
        return cache_data

    # Location skipped if in db
    db_data = await check_db(norm_loc)
    if db_data:
        logging.info(f"Database hit: {norm_loc}")
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

        #Save into cache
        save_in_cache(norm_loc, lat, lng) 

        #Save into db
        await save_in_db(norm_loc, lat, lng)
        logging.info(f"{norm_loc} geocoded as ({lat}, {lng})")
        return {'norm_loc': norm_loc, 'lat': lat, 'lng': lng }
    
    logging.error(f"Failed to geocode: {location} (no results returned)")
    return None

async def geocode_locations(df):

    #respecting rate limit with semaphore
    semaphore = asyncio.Semaphore(MAX_RPS)
    try: 
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_geocode(session, location, semaphore) for location in df["location"]]
            await asyncio.gather(*tasks)
    except Exception as e:
        logging.error(f"Error in geocoding locations: {e}")

#Main function
async def main():
    logging.info("Starting program...")

    #r.flushall() for testing purposes only
    df = fetch_data()
    if not df.empty:
        logging.info(f"Fetched {len(df)} posts from API.")
    else:
        logging.info("Failed to fetch data from API.")
    df_cleaned = df[['location']].dropna().drop_duplicates()

    #Loading data asynchronously to speed up process
    if (r.dbsize() < 60754):
        await asyncio.gather(
        load_csv("uscities.csv"),
        load_csv("worldcities.csv")
        )
    else:
        logging.info("Redis cache already populated with uscities.csv and worldcities.csv.")

    #Testing purposes only
    logging.info(f"Redis db size: {r.dbsize()}")
    logging.info(f"Data for 'Los Angeles': {r.hgetall('Los Angeles')}")
    logging.info(f"Data for 'Semič': {r.hgetall('Semič')}")

    logging.info(f"Process geocoding of {len(df_cleaned)} locations...")
    await geocode_locations(df_cleaned)

# Run the main function
if __name__ == "__main__":
    asyncio.run(main()) 
    

