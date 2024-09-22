import asyncio
import os
import httpx
import json
from dotenv import load_dotenv
from redis.asyncio import Redis
from fastapi import HTTPException
from components.custom_logger import get_logger
from datetime import datetime, timezone, timedelta

from db.mdb_client import booking_db

load_dotenv()

logger = get_logger("rapidapi_client")
timezone_offset_hours = int(os.getenv("TIMEZONE_OFFSET_HOURS", 0))  # Default to UTC (0)
env_expire_hours = int(os.getenv("EXPIRE_HOURS", 72))  # Default to 72 hours


async def fetch_and_cache(url, headers, params, cache_key, expire_seconds, redis: Redis, collection,
                          expire_hours: int = env_expire_hours):
    """
    Fetch data from MongoDB or API and cache it in Redis. The document is fetched from the API if expired.
    """

    # Log the start of the operation
    logger.info("Attempting to load data from MongoDB for params: %s", params)

    # First, try to find the document in MongoDB using the params
    document = await booking_db[collection].find_one(params)

    # Check if the document exists and whether it has expired
    if document:
        created_at = document.get("created_at")
        if created_at:
            created_at_datetime = datetime.fromisoformat(created_at)  # Parse the ISO format datetime
            expire_datetime = created_at_datetime + timedelta(hours=expire_hours)

            # Check if the current time has passed the expiration date
            current_time_with_offset = datetime.now(timezone(timedelta(hours=timezone_offset_hours)))
            if current_time_with_offset < expire_datetime:
                # Document is still valid, return the cached data
                logger.info("Data found in MongoDB for params: %s", params)
                return document.get("data")
            else:
                logger.info("Document expired for params: %s, fetching fresh data", params)
        else:
            logger.warning("Document for params: %s found but missing 'created_at' field", params)
    else:
        logger.info("No data found in MongoDB. Fetching data from API for params: %s", params)

    # Fetch data from the API if the document does not exist or is expired
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()  # Automatically raise HTTPException for non-200 responses
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    # Cache the response in Redis
    await redis.set(cache_key, response.text, ex=expire_seconds)
    logger.info("Data fetched from API and cached in Redis with key: %s", cache_key)

    # Insert the new data and updated 'created_at' into MongoDB
    current_time_with_offset = datetime.now(timezone(timedelta(hours=timezone_offset_hours)))
    document_to_insert = {
        **params,  # Spread the params directly into the document
        "data": response.json(),  # Add the response data
        "created_at": current_time_with_offset.isoformat()  # Use timezone-aware datetime
    }

    await booking_db[collection].replace_one(params, document_to_insert, upsert=True)
    logger.info("Data inserted or updated in MongoDB for params: %s", params)

    return response.json()


# Helper function to get data from Redis or fetch and cache it
async def get_data_or_cache(endpoint, params, cache_key, expire_seconds, redis, expire_hours: int = env_expire_hours):
    """
    Get data from Redis or fetch and cache it if not available.

    Args:
        expire_hours:
        endpoint (str): The API endpoint to fetch data from.
        params (dict): The query parameters to include in the API request.
        cache_key (str): The key to use for caching the response in Redis.
        expire_seconds (int): The expiration time for the cached data in seconds.
        redis (Redis): The Redis client instance.

    Returns:
        dict: The JSON response from the API or cached data.
    """
    # Check if data exists in the cache
    cached_data = await redis.get(cache_key)
    if cached_data:
        return json.loads(cached_data)

    # Construct the API URL
    url = f"https://{os.getenv('RAPIDAPI_HOST')}/api/v1/hotels/{endpoint}"

    # API request headers
    headers = {
        'x-rapidapi-key': os.getenv("RAPIDAPI_KEY"),
        'x-rapidapi-host': os.getenv("RAPIDAPI_HOST")
    }

    # Fetch the data and cache it
    return await fetch_and_cache(url, headers, params, cache_key, expire_seconds, redis, endpoint, expire_hours)


# Test block
if __name__ == "__main__":
    async def main():
        redis = Redis(host='localhost', port=6379, db=0)  # Adjust your Redis configuration

        # Example test data matching your curl request
        endpoint = "reviews"
        params = {
            'sort_type': 'SORT_MOST_RELEVANT',
            'page_number': 0,
            'hotel_id': 4469654,
            'locale': 'en-gb',
            'customer_type': 'solo_traveller,review_category_group_of_friends',
            'language_filter': 'he'
        }
        cache_key = "hotel_reviews_4469654"
        expire_seconds = 3600  # Cache expiry time (e.g., 1 hour)

        try:
            # Use the get_data_or_cache helper function
            result = await get_data_or_cache(endpoint, params, cache_key, expire_seconds, redis)

            # Pretty print the JSON response
            print("API Response (Prettified):")
            print(json.dumps(result, indent=4))

            # Fetch and pretty print the cached value
            cached_value = await redis.get(cache_key)
            if cached_value:
                print("\nCached Value (Prettified):")
                print(json.dumps(json.loads(cached_value.decode()), indent=4))
            else:
                print("No cache found")
        except HTTPException as e:
            print(f"HTTPException: {e.detail}")


    # Run the test
    asyncio.run(main())
