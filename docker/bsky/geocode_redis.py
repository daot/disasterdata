import pandas as pd
import redis
import csv
import logging
import os
import asyncio
import re
import us
from urllib.parse import urlparse
#from retrying import retry


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
    "new york": "New York City"
}


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

def save_in_cache(norm_loc, lat, lng, redis_cli):
    """Save geocoded location into Redis cache."""
    redis_cli.hset(norm_loc, mapping={"lat": lat, "lng": lng})
    logging.info(f"Saved {norm_loc} into Redis with coordinates: ({lat}, {lng})")

def check_cache(norm_loc, redis_cli):
    #Check if location is in Redis cache
    if redis_cli.exists(norm_loc):
        coordinates = redis_cli.hgetall(norm_loc)
        logging.info(f"Cache hit for {norm_loc}: {coordinates} found in Redis")
        return norm_loc, coordinates.get("lat"), coordinates.get("lng")
    return None 

#@retry(stop_max_attempt_number=5, wait_fixed=2000)
async def fetch_geocode(session, location, semaphore, redis_cli, GEOCODE_URL, API_KEY):
    """Checks cache first and geocodes and saves back into cache if location is not is not there"""
    if location is None:
        return None, None, None

    #Location skipped if in cache
    norm_loc = normalize_location(location)
    cache_data = check_cache(norm_loc, redis_cli)
    if cache_data:  
        #logging.info(f"Cache hit: {norm_loc}")
        return cache_data
    
    #Only allowing 5 concurrent tasks
    async with semaphore:
        try:
            async with session.get(GEOCODE_URL.format(norm_loc, API_KEY)) as response: 
                if response.status == 200:
                    data = await response.json()
                else:
                    logging.error(f"Failed to geocode location for {location} with Status Code: {response.status}")
                    return location, None, None
        except Exception as e:
            logging.warning(f"Error in retrieving coordinates for {location} with {e}")
            return location, None, None

    #Matching the HERE API response format
    if data.get("items"):  
        lat = data["items"][0]["position"]["lat"]
        lng = data["items"][0]["position"]["lng"]

        #Save into cache
        save_in_cache(norm_loc, lat, lng, redis_cli) 

        logging.info(f"{norm_loc} geocoded as ({lat}, {lng})")
        #return {'norm_loc': norm_loc, 'lat': lat, 'lng': lng }
        return norm_loc, lat, lng
    
    logging.error(f"Failed to geocode: {location} (no results returned)")
    return location, None, None


