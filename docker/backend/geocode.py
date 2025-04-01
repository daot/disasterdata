import pandas as pd
import requests
import sqlite3
import asyncio
import aiohttp
import re
from dotenv import load_dotenv
import os
from rapidfuzz import process, fuzz
import logging


load_dotenv()

API_URL=os.getenv('API_URL') #Database URL
CACHE_FILE=os.getenv('CACHE_FILE')
API_KEY=os.getenv('API_KEY')
geocode_url=os.getenv('geocode_url') #Using HERE API
MAX_RPS=5 #Maximum of 5 requests per second 


#Logger to save debugging output
logging.basicConfig(
    filename="geocode_debug.log",
    level=logging.INFO,
    filemode="w",
    format="%(asctime)s %(message)s"
)

ABBREV= {
    "us": "United States",
    "usa": "United States",
    "la county": "LA County",
    "la": "Los Angeles",
    "dc": "Washington D.C.",
    "sf": "San Francisco",
    "chi-town": "Chicago"
}
#Fetching data from the database
async def fetch_data():
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL) as response:
            if response.status != 200:
                return (pd.DataFrame(), response.status)
            else:
                data = await response.json()
                posts = data.get("posts", [])
                return (pd.DataFrame(posts), response.status)

#Create cache table (will change to posgresql table)
def create_cache():
    with sqlite3.connect(CACHE_FILE) as conn:
        cursor = conn.cursor()
        conn.execute("""CREATE TABLE IF NOT EXISTS locations(
        standard_location TEXT UNIQUE,
        latitude REAL,
        longitude REAL)""")
    return True

#Checking whether the location is already cached
def check_cache(norm_loc):
    with sqlite3.connect(CACHE_FILE) as conn:
        logging.info(f"Checking location {norm_loc} in cache")
        cursor = conn.cursor()

        #Check using exact match
        cursor.execute("""SELECT standard_location, latitude, longitude 
        FROM locations WHERE standard_location = ?""",
        (norm_loc,))
        cache_result = cursor.fetchone()
        if cache_result is not None:
            return cache_result
        
        #List of all locations so far
        cursor.execute("""SELECT standard_location FROM locations""")
        known_locations = [row[0] for row in cursor.fetchall()]

        #Account for misspellings using RapidFuzz
        match, score, temp = process.extractOne(norm_loc, known_locations, scorer=fuzz.ratio) if known_locations else (None, 0, None)
        if match and score > 85:
            cursor.execute("""SELECT standard_location, latitude, longitude 
            FROM locations 
            WHERE standard_location = ?""", 
            (match,))
            fuzzy_match = cursor.fetchone()
            return fuzzy_match
    return None

#Saving new coordinates into cache
def save_in_cache(standard_location, latitude, longitude):
    with sqlite3.connect(CACHE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""INSERT OR IGNORE INTO locations (standard_location, latitude, longitude) 
        VALUES (?, ?, ?)""", 
        (standard_location, latitude, longitude))
        conn.commit()
    logger.info(f"{standard_location} saved into db")


def duplicates_in_cache():
    with sqlite3.connect(CACHE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""SELECT standard_location, COUNT(*) as count 
        FROM locations 
        GROUP BY standard_location 
        HAVING count > 1;
        """)
        results = cursor.fetchall()
        return results

def normalize_location(location):
    location = location.lower()
    
    #Removing punctuation or whitespace
    location = re.sub(r'[^a-zA-Z0-9\s]', '', location)
    location = re.sub(r'\s+', ' ', location).strip()

    return cleaned_location.title() 

async def fetch_geocode(session, location, semaphore):

    #Location skipped if in cache
    norm_loc = normalize_location(location)
    if check_cache(norm_loc) is not None:  
        logging.info(f"Cache hit: {norm_loc}")
        return None 
    
    #Only allowing 5 concurrent tasks
    async with semaphore:
        try:
            async with session.get(geocode_url.format(location, API_KEY)) as response: #q is location param
                if response.status == 200:
                    data = await response.json()
                else:
                    logging.info(f"Failed to geocode location for {norm_loc} with Status Code: {response.status}")
                    return None
        except Exception as e:
            logging.info(f"Error in retrieving coordinates for {norm_loc} with {e}")
            return None
    
    #Matching the HERE API response format
    if data.get("items"):  
        lat = data["items"][0]["position"]["lat"]
        lng = data["items"][0]["position"]["lng"]
        API_loc = data["items"][0]["address"]["label"]

        #Save into cache and database
        save_in_cache(norm_loc, lat, lng) 

        #update_posgresql function will be implemented
        logging.info(f"{norm_loc} geocoded as {API_loc} or ({lat}, {lng})")
        return (norm_loc, lat, lng)
    
    logging.info(f"Failed to geocode: {norm_loc}")
    return None

async def geocode_locations(df):

    #respecting rate limit with semaphore
    semaphore = asyncio.Semaphore(MAX_RPS)  
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_geocode(session, location, semaphore) for location in df["location"]]

        #process results once complete
        for task in asyncio.as_completed(tasks):
           result = await task

async def main():
    df, status_code = await fetch_data()
    if df.empty:
        logging.info(f"No data found. HTTP status code {status_code}")
    else:
        logging.info("Data fetched successfully.")

        #Extracting only non-null, unique locations
        df_cleaned = df[['location']].dropna().drop_duplicates().reset_index(drop=True) 
        logging.info(f"Processing {df_cleaned.size} locations...")
        await geocode_locations(df_cleaned)

if __name__ == "__main__":
    if os.path.exists(CACHE_FILE):
        logging.info("NEW RUN: Cache file already exists, skipping create_cache()")
    elif create_cache():
        logging.info("NEW RUN: Cache file creation successful")
    asyncio.run(main())
    