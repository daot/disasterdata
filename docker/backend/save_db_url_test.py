import requests
import logging
import asyncio
import aiohttp
from urllib.parse import urlparse

DB_URL="http://disasterdata.duckdns.org:5001"
logging.basicConfig(
    filename="save_db__url_test.log",
    level=logging.DEBUG,
    filemode="w",
    format="%(asctime)s %(message)s"
)
async def save_in_db(norm_loc, lat, lng, session):
    #Save the location in the db
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
                logging.error(f"Failed to save location {norm_loc} to database. Status code: {response.status} (location in database)")
    except Exception as e:
        logging.error(f"Error saving location {norm_loc} to database: {e}")

def is_url(string):
    try:
        #Prepend scheme if missing
        if not string.startswith(('http://', 'https://')):
            string = 'http://' + string

        result = urlparse(string)
        netloc = result.netloc.lower()

        #Valid URL if netloc contains at least one dot and isn't just www.
        return bool(netloc and '.' in netloc and netloc != 'www.')
    except Exception:
        return False

async def test_save_in_db():
    sample_URLS = [ 
        "cheeseburgers",
        "https://www.example.com",
        "Alaska",
        "bmcnoldy.blogspot.com/2025/04/3-na",
        "www.c4pmc.co.uk/post/nationa",
        "http://www.bom.gov.au/nsw/warnings/flood/orarariver.shtml"
    ]
    for url in sample_data:
        if is_url(url):
            print(f"{url} is a valid URL")
        else:
            print(f"{url} is not a valid URL")

    sample_data = [
        ("Dummy", -28.26343, 168.13794),
        ("Lumbini", 27.9207, 82.7347),
        ("Tokyo", 35.6897, 139.6922)
    ]

    async with aiohttp.ClientSession() as session:
        for norm_loc, lat, lng in sample_data:
            await save_in_db(norm_loc, lat, lng, session)
    
# Run it
if __name__ == "__main__":
    asyncio.run(test_save_in_db())
    main()
