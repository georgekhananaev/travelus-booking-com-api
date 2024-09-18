import asyncio
import os
import httpx
import json
from dotenv import load_dotenv
from redis.asyncio import Redis
from fastapi import HTTPException
from components.custom_logger import get_logger

from db.mdb_client import booking_db

load_dotenv()

logger = get_logger("rapidapi_client")


# async def fetch_and_cache(url, headers, params, cache_key, expire_seconds, redis, collection):
#     """
#     Example async function that fetches data, caches it in Redis, and logs asynchronously.
#     """
#     logger = await get_logger("my_logger")
#
#     # Log the start of the operation
#     logger.info(f"Attempting to load data from MongoDB for params: {params}")
#
#     # Try to find the document in MongoDB
#     document = await booking_db[collection].find_one(params)
#
#     if document:
#         logger.info(f"Data found in MongoDB for params: {params}")
#         return document.get("data")
#
#     # If not found, fetch from the API
#     logger.info(f"No data found in MongoDB. Fetching data from API for params: {params}")
#
#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(url, headers=headers, params=params)
#             response.raise_for_status()  # Automatically raise an exception for non-200 responses
#         except httpx.HTTPStatusError as e:
#             logger.error(f"HTTP error occurred: {e.response.text}")
#             raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
#         except Exception as e:
#             logger.error(f"An error occurred: {str(e)}")
#             raise HTTPException(status_code=500, detail=str(e))
#
#     # Cache the response in Redis
#     await redis.set(cache_key, response.text, ex=expire_seconds)
#     logger.info(f"Data fetched from API and cached in Redis with key: {cache_key}")
#
#     # Insert both the params and the response JSON into MongoDB
#     document_to_insert = {**params, "data": response.json()}
#     await booking_db[collection].insert_one(document_to_insert)
#     logger.info(f"Data inserted into MongoDB for params: {params}")
#
#     return response.json()


# async def fetch_and_cache(url, headers, params, cache_key, expire_seconds, redis):
#     """
#     Example async function that fetches data, caches it in Redis, and logs asynchronously.
#     """
#     logger = await get_logger("my_logger")
#
#     # Log the start of the operation
#     await logger.info(f"Attempting to load data from MongoDB for params: {params}")
#
#     # Try to find the document in MongoDB
#     document = await booking_db.photos.find_one(params)
#
#     if document:
#         await logger.info(f"Data found in MongoDB for params: {params}")
#         return document.get("data")
#
#     # If not found, fetch from the API
#     await logger.info(f"No data found in MongoDB. Fetching data from API for params: {params}")
#
#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(url, headers=headers, params=params)
#             response.raise_for_status()  # Automatically raise an exception for non-200 responses
#         except httpx.HTTPStatusError as e:
#             await logger.error(f"HTTP error occurred: {e.response.text}")
#             raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
#         except Exception as e:
#             await logger.error(f"An error occurred: {str(e)}")
#             raise HTTPException(status_code=500, detail=str(e))
#
#     # Cache the response in Redis
#     await redis.set(cache_key, response.text, ex=expire_seconds)
#     await logger.info(f"Data fetched from API and cached in Redis with key: {cache_key}")
#
#     # Insert both the params and the response JSON into MongoDB
#     document_to_insert = {**params, "data": response.json()}
#     await booking_db.photos.insert_one(document_to_insert)
#     await logger.info(f"Data inserted into MongoDB for params: {params}")
#
#     return response.json()


async def fetch_and_cache(url, headers, params, cache_key, expire_seconds, redis: Redis, collection):
    """
    Fetch data from MongoDB or API and cache it in Redis.
    """

    # Log the start of the operation
    logger.info("Attempting to load data from MongoDB for params: %s", params)

    # First, try to find the document in MongoDB using the params
    document = await booking_db[collection].find_one(params)

    if document:
        # If the document is found in MongoDB, return the 'data' field
        logger.info("Data found in MongoDB for params: %s", params)
        return document.get("data")

    # If not found in MongoDB, proceed to fetch from the API
    logger.info("No data found in MongoDB. Fetching data from API for params: %s", params)
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

    # Insert both the params and the response JSON into MongoDB
    document_to_insert = {
        **params,  # Spread the params directly into the document
        "data": response.json()  # Add the response data
    }
    await booking_db[collection].insert_one(document_to_insert)
    logger.info("Data inserted into MongoDB for params: %s", params)

    return response.json()


# async def fetch_and_cache(url, headers, params, cache_key, expire_seconds, redis: Redis):
#     """
#     Fetch data from MongoDB or API and cache it in Redis.
#
#     Args:
#         url (str): The API endpoint URL.
#         headers (dict): The headers to include in the API request.
#         params (dict): The query parameters to include in the API request.
#         cache_key (str): The key to use for caching the response in Redis.
#         expire_seconds (int): The expiration time for the cached data in seconds.
#         redis (Redis): The Redis client instance.
#         booking_db (MongoDB): The MongoDB client instance.
#
#     Returns:
#         dict: The JSON response from the API or MongoDB.
#
#     Raises:
#         HTTPException: If the API response status code is not 200.
#     """
#
#     # First, try to find the document in MongoDB using the params
#     document = await booking_db.photos.find_one(params)
#
#     if document:
#         # If the document is found in MongoDB, return the 'data' field
#         return document.get("data")
#
#     # If not found in MongoDB, proceed to fetch from the API
#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(url, headers=headers, params=params)
#             response.raise_for_status()  # Automatically raise HTTPException for non-200 responses
#         except httpx.HTTPStatusError as e:
#             print(f"HTTP error occurred: {e.response.text}")
#             raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
#         except Exception as e:
#             print(f"An error occurred: {str(e)}")
#             raise HTTPException(status_code=500, detail=str(e))
#
#     # Cache the response in Redis
#     await redis.set(cache_key, response.text, ex=expire_seconds)
#
#     # Only insert a new document into MongoDB if the data was fetched from the API
#     document_to_insert = {
#         **params,  # Spread the params directly into the document
#         "data": response.json()  # Add the response data
#     }
#     await booking_db.photos.insert_one(document_to_insert)
#
#     return response.json()

# async def fetch_and_cache(url, headers, params, cache_key, expire_seconds, redis: Redis):
#     """
#     Fetch data from the API and cache it in Redis.
#
#     Args:
#         url (str): The API endpoint URL.
#         headers (dict): The headers to include in the API request.
#         params (dict): The query parameters to include in the API request.
#         cache_key (str): The key to use for caching the response in Redis.
#         expire_seconds (int): The expiration time for the cached data in seconds.
#         redis (Redis): The Redis client instance.
#
#     Returns:
#         dict: The JSON response from the API.
#
#     Raises:
#         HTTPException: If the API response status code is not 200.
#     """
#
#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(url, headers=headers, params=params)
#             response.raise_for_status()  # Automatically raise HTTPException for non-200 responses
#         except httpx.HTTPStatusError as e:
#             print(f"HTTP error occurred: {e.response.text}")
#             raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
#         except Exception as e:
#             print(f"An error occurred: {str(e)}")
#             raise HTTPException(status_code=500, detail=str(e))
#
#     # If the request is successful, cache the response
#     await redis.set(cache_key, response.text, ex=expire_seconds)
#
#     # Insert both the params and the response JSON into MongoDB
#     document_to_insert = {
#         **params,  # Spread the params directly into the document
#         "data": response.json()  # Add the response data
#     }
#
#     await booking_db.photos.insert_one(document_to_insert)
#
#     return response.json()


# Helper function to get data from Redis or fetch and cache it
async def get_data_or_cache(endpoint, params, cache_key, expire_seconds, redis):
    """
    Get data from Redis or fetch and cache it if not available.

    Args:
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
    return await fetch_and_cache(url, headers, params, cache_key, expire_seconds, redis, endpoint)


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
