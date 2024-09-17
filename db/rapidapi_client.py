import asyncio
import os
import httpx
import json
from dotenv import load_dotenv
from redis.asyncio import Redis
from fastapi import HTTPException

load_dotenv()


async def fetch_and_cache(url, headers, params, cache_key, expire_seconds, redis: Redis):
    """
    Fetch data from the API and cache it in Redis.

    Args:
        url (str): The API endpoint URL.
        headers (dict): The headers to include in the API request.
        params (dict): The query parameters to include in the API request.
        cache_key (str): The key to use for caching the response in Redis.
        expire_seconds (int): The expiration time for the cached data in seconds.
        redis (Redis): The Redis client instance.

    Returns:
        dict: The JSON response from the API.

    Raises:
        HTTPException: If the API response status code is not 200.
    """

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()  # Automatically raise HTTPException for non-200 responses
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    # If the request is successful, cache the response
    await redis.set(cache_key, response.text, ex=expire_seconds)
    return response.json()


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
    return await fetch_and_cache(url, headers, params, cache_key, expire_seconds, redis)


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
