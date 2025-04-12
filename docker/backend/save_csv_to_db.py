import pandas as pd
import asyncio
import logging
import aiohttp

# Your server URL
DB_URL = "http://disasterdata.duckdns.org:5001"

# Limit how many requests are running at once
semaphore = asyncio.Semaphore(20)

# Setup logging
logging.basicConfig(
    filename="geocode_debug.log",
    level=logging.DEBUG,
    filemode="w",
    format="%(asctime)s %(message)s"
)

async def check_db(session, norm_loc):
    """Check if location is already in the database."""
    try:
        async with session.get(f'{DB_URL}/get_location?norm_loc={norm_loc}') as response:
            if response.status == 200:
                logging.info(f"Location {norm_loc} found in the database.")
                return await response.json()  # Must await here
            elif response.status == 404:
                logging.info(f"Location {norm_loc} not found in the database.")
                return None
            else:
                logging.error(f"Error checking database for {norm_loc}. Status code: {response.status}")
                return None
    except Exception as e:
        logging.error(f"Exception during DB check for {norm_loc}: {e}")
        return None

async def save_in_db(session, norm_loc, lat, lng):
    """Save location to the DB using the shared aiohttp session."""
    data = {
        'norm_loc': norm_loc,
        'lat': lat,
        'lng': lng
    }
    try:
        async with session.post(f'{DB_URL}/add_location', data=data) as response:
            if response.status == 201:
                logging.info(f"Location {norm_loc} saved to database")
            else:
                logging.error(f"Failed to save location {norm_loc}. Status code: {response.status}")
    except Exception as e:
        logging.error(f"Error saving location {norm_loc} to database: {e}")

async def throttled_check_and_save(session, norm_loc, lat, lng):
    """Throttled wrapper to check DB and save if not found."""
    async with semaphore:
        result = await check_db(session, norm_loc)
        if result is None:
            await save_in_db(session, norm_loc, lat, lng)
        else:
            logging.info(f"Skipping {norm_loc}, already in DB.")

async def load_csv(filename, session):
    """Load CSV data and save each city to the database asynchronously."""
    logging.info(f"Processing {filename}...")
    df = pd.read_csv(filename, usecols=["city", "lat", "lng"], sep=",")
    df = df.drop_duplicates(subset=["city"])

    logging.info(f"Loaded {len(df)} rows from {filename}.")

    tasks = []
    for _, row in df.iterrows():
        city = row["city"]
        lat = row["lat"]
        lng = row["lng"]
        logging.info(f"Queueing {city} with lat={lat}, lng={lng}")
        tasks.append(throttled_check_and_save(session, city, lat, lng))

    await asyncio.gather(*tasks)
    logging.info(f"Finished processing {filename}.")

async def main():
    async with aiohttp.ClientSession() as session:
        await load_csv("worldcities.csv", session)

if __name__ == "__main__":
    asyncio.run(main())