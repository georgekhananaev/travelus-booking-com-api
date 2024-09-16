from fastapi import APIRouter, Depends, HTTPException
import os
import json
import httpx
from datetime import datetime, timedelta
from redis.asyncio import Redis

from db.clientRedis import AsyncRedisClient

router = APIRouter()


# Function to fetch data from the API and cache it in Redis
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
        response = await client.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    await redis.set(cache_key, response.text, ex=expire_seconds)
    return response.json()


# Helper function to get data from Redis or fetch and cache it
async def get_data_or_cache(endpoint, hotel_id, locale, params, cache_key, expire_seconds, redis):
    """
    Get data from Redis or fetch and cache it if not available.

    Args:
        endpoint (str): The API endpoint to fetch data from.
        hotel_id (int): The ID of the hotel.
        locale (str): The locale for the data.
        params (dict): The query parameters to include in the API request.
        cache_key (str): The key to use for caching the response in Redis.
        expire_seconds (int): The expiration time for the cached data in seconds.
        redis (Redis): The Redis client instance.

    Returns:
        dict: The JSON response from the API or cached data.
    """
    cached_data = await redis.get(cache_key)
    if cached_data:
        return json.loads(cached_data)

    url = f"https://{os.getenv('RAPIDAPI_HOST')}/v1/hotels/{endpoint}"
    headers = {
        'x-rapidapi-key': os.getenv("RAPIDAPI_KEY"),
        'x-rapidapi-host': os.getenv("RAPIDAPI_HOST")
    }
    return await fetch_and_cache(url, headers, params, cache_key, expire_seconds, redis)


# Endpoint to get hotel photos
@router.get("/photos")
async def get_hotel_photos(hotel_id: int = 4469654, locale: str = "en-gb",
                           redis: Redis = Depends(AsyncRedisClient.get_instance)):
    """
    Endpoint to get hotel photos.

    Args:
        hotel_id (int): The ID of the hotel.
        locale (str): The locale for the data.
        redis (Redis): The Redis client instance.

    Returns:
        dict: The JSON response containing hotel photos.
    """
    params = {'hotel_id': hotel_id, 'locale': locale}
    cache_key = f"hotel_photos_{hotel_id}_{locale}"
    return await get_data_or_cache("photos", hotel_id, locale, params, cache_key,
                                   int(timedelta(hours=24).total_seconds()), redis)


# Endpoint to get hotel data
@router.get("/data")
async def get_hotel_data(hotel_id: int = 4469654, locale: str = "en-gb",
                         redis: Redis = Depends(AsyncRedisClient.get_instance)):
    """
    Endpoint to get hotel data.

    Args:
        hotel_id (int): The ID of the hotel.
        locale (str): The locale for the data.
        redis (Redis): The Redis client instance.

    Returns:
        dict: The JSON response containing hotel data.
    """
    params = {'hotel_id': hotel_id, 'locale': locale}
    cache_key = f"hotel_data_{hotel_id}_{locale}"
    return await get_data_or_cache("data", hotel_id, locale, params, cache_key,
                                   int(timedelta(hours=24).total_seconds()), redis)


# Endpoint to get hotel reviews
@router.get("/reviews")
async def get_hotel_reviews(
        hotel_id: int = 4469654,
        locale: str = "en-gb",
        customer_type: str = "solo_traveller,review_category_group_of_friends",
        sort_type: str = "SORT_MOST_RELEVANT",
        language_filter: str = "he",
        page_number: int = 0,
        redis: Redis = Depends(AsyncRedisClient.get_instance)
):
    """
    Endpoint to get hotel reviews.

    Args:
        hotel_id (int): The ID of the hotel.
        locale (str): The locale for the data.
        customer_type (str): The type of customer for the reviews.
        sort_type (str): The sorting type for the reviews.
        language_filter (str): The language filter for the reviews.
        page_number (int): The page number for the reviews.
        redis (Redis): The Redis client instance.

    Returns:
        dict: The JSON response containing hotel reviews.
    """
    params = {
        'hotel_id': hotel_id,
        'locale': locale,
        'customer_type': customer_type,
        'sort_type': sort_type,
        'language_filter': language_filter,
        'page_number': page_number
    }
    cache_key = f"hotel_reviews_{hotel_id}_{locale}_{customer_type}_{sort_type}_{language_filter}_{page_number}"
    return await get_data_or_cache("reviews", hotel_id, locale, params, cache_key,
                                   int(timedelta(hours=24).total_seconds()), redis)


# Endpoint to get hotel room list
@router.get("/room-list")
async def get_hotel_room_list(
        hotel_id: int = 4469654,
        checkin_date: str = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
        checkout_date: str = (datetime.now() + timedelta(days=31)).strftime('%Y-%m-%d'),
        children_ages: str = "5,0,9",
        children_number_by_rooms: str = "2,1",
        adults_number_by_rooms: str = "3,1",
        units: str = "metric",
        currency: str = "THB",
        locale: str = "en-gb",
        redis: Redis = Depends(AsyncRedisClient.get_instance)
):
    """
    Endpoint to get hotel room list.

    Args:
        hotel_id (int): The ID of the hotel.
        checkin_date (str): The check-in date for the room list.
        checkout_date (str): The check-out date for the room list.
        children_ages (str): The ages of the children.
        children_number_by_rooms (str): The number of children by rooms.
        adults_number_by_rooms (str): The number of adults by rooms.
        units (str): The units for the data (e.g., metric).
        currency (str): The currency for the data.
        locale (str): The locale for the data.
        redis (Redis): The Redis client instance.

    Returns:
        dict: The JSON response containing hotel room list.
    """
    params = {
        'hotel_id': hotel_id,
        'checkin_date': checkin_date,
        'checkout_date': checkout_date,
        'children_ages': children_ages,
        'children_number_by_rooms': children_number_by_rooms,
        'adults_number_by_rooms': adults_number_by_rooms,
        'units': units,
        'currency': currency,
        'locale': locale
    }
    cache_key = f"hotel_room_list_{hotel_id}_{checkin_date}_{checkout_date}_{children_ages}_{children_number_by_rooms}_{adults_number_by_rooms}_{units}_{currency}_{locale}"
    return await get_data_or_cache("room-list", hotel_id, locale, params, cache_key,
                                   int(timedelta(hours=8).total_seconds()), redis)
