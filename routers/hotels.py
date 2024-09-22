import asyncio
import os
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Request, Query
from datetime import datetime
from db.rapidapi_client import get_data_or_cache
from datetime import timedelta
from redis.asyncio import Redis

from db.redis_client import AsyncRedisClient
from components.transform_data import transform_data, transform_room_data
from models.detailed_hotel import DetailedHotelResponse
from models.hotels import HotelsResponse, Hotel
from models.photos import Photo
from models.reviews import Review
from models.rooms import RoomsData

router = APIRouter()

load_dotenv()
mongo_expire_hours = int(os.getenv("EXPIRE_HOURS", 72))  # Default to 72 hours
redis_expire_seconds = int(os.getenv("EXPIRE_SECONDS", 5))  # Default to 5 seconds


# Endpoint to get hotel data
@router.get("/hotel")
async def get_hotel_data(
        hotel_id: int = 4469654,
        locale: str = "en-gb",
        redis: Redis = Depends(AsyncRedisClient.get_instance),
        expire_hours: int = mongo_expire_hours
):
    params = {'hotel_id': hotel_id, 'locale': locale}
    cache_key = f"hotel_data_{hotel_id}_{locale}"

    # Fetch the hotel data, either from cache or source
    hotel_data = await get_data_or_cache("data", params, cache_key, redis_expire_seconds, redis, expire_hours)

    # Ensure the data matches the Pydantic model structure
    hotel = Hotel(**hotel_data)

    return hotel


# Fetch multiple hotels' data concurrently
@router.get("/hotels/", response_model=HotelsResponse)
async def get_multiple_hotels_data(
        hotel_ids: List[int] = Query(default=[2534439, 4469654], alias="hotel_ids"),
        locale: str = "en-gb",
        redis: Redis = Depends(AsyncRedisClient.get_instance),  # Redis dependency
        expire_hours: int = 72  # Expiry in hours
):
    # Gather hotel data for each ID
    results = await asyncio.gather(
        *[get_hotel_data(hotel_id=hotel_id, locale=locale, redis=redis, expire_hours=expire_hours)
          for hotel_id in hotel_ids]
    )

    # Convert the results into the HotelsResponse model
    hotels = [hotel_data for hotel_data in results]

    return {"hotels": hotels}


# Endpoint to get hotel photos
@router.get("/photos", response_model=List[Photo])
async def get_hotel_photos(
        req: Request,
        hotel_id: int = 4469654,
        locale: str = "en-gb",
        expire_hours: int = mongo_expire_hours
):
    redis = req.app.redis_client
    params = {'hotel_id': hotel_id, 'locale': locale}
    cache_key = f"hotel_photos_{hotel_id}_{locale}"

    # Fetch the data from cache or API, this function should return a list of photo data
    photos_data = await get_data_or_cache("photos", params, cache_key, redis_expire_seconds, redis, expire_hours)

    # Return the photos list, Pydantic will validate the structure against the Photo model
    return photos_data


# Endpoint to get hotel reviews
@router.get("/reviews", response_model=List[Review])
async def get_hotel_reviews(
        hotel_id: int = 4469654,
        locale: str = "en-gb",
        customer_type: str = "solo_traveller,review_category_group_of_friends",
        sort_type: str = "SORT_MOST_RELEVANT",
        language_filter: str = "en-us",
        page_number: int = 0,
        redis: Redis = Depends(AsyncRedisClient.get_instance),
        expire_hours: int = mongo_expire_hours
):
    params = {
        'hotel_id': hotel_id,
        'locale': locale,
        'customer_type': customer_type,
        'sort_type': sort_type,
        'language_filter': language_filter,
        'page_number': page_number
    }
    cache_key = f"hotel_reviews_{hotel_id}_{locale}_{customer_type}_{sort_type}_{language_filter}_{page_number}"

    # Fetch data from cache or external API
    response_data = await get_data_or_cache("reviews", params, cache_key, redis_expire_seconds, redis, expire_hours)

    # Assuming the actual reviews are nested under a 'result' key, extract them
    # You might need to adjust 'result' to match the actual structure you're receiving
    if isinstance(response_data, dict) and 'result' in response_data:
        reviews_data = response_data['result']  # Adjust if reviews are under a different key
    else:
        reviews_data = response_data  # If the structure is already correct

    # Ensure the data is a list before returning
    if not isinstance(reviews_data, list):
        raise ValueError("Expected list of reviews, but got something else")

    return reviews_data


# Endpoint to get hotel room list
@router.get("/room-list", response_model=Optional[List[RoomsData]])
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
        redis: Redis = Depends(AsyncRedisClient.get_instance),
        expire_hours: int = 8  # Adjust the expiration hours based on your env setting
):
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

    # Create a cache key based on the parameters
    cache_key = f"hotel_room_list_{hotel_id}_{checkin_date}_{checkout_date}_{children_ages}_{children_number_by_rooms}_{adults_number_by_rooms}_{units}_{currency}_{locale}"

    # Fetch data or use the cached result
    hotel_data = await get_data_or_cache("room-list", params, cache_key, redis_expire_seconds, redis, expire_hours)

    # Ensure hotel_data is a list
    if isinstance(hotel_data, list):
        return [RoomsData(**room) for room in
                hotel_data]  # Iterate over the list and initialize RoomsData for each item

    # Handle the case where hotel_data is not a list
    if hotel_data:
        return [RoomsData(**hotel_data)]  # Wrap in a list to match the response_model type
    return None  # If no data, return None or appropriate response


@router.get("/detailed_hotel", response_model=List[DetailedHotelResponse])
async def mock_detail_hotel(
        hotel_ids: List[int] = Query(default=[4469654]),  # Accept a list of hotel IDs
        redis: Redis = Depends(AsyncRedisClient.get_instance),
        expire_hours: int = 72,  # Default to 72 hours if not provided
        show_photos: bool = True,  # Add show_photos parameter with default True
        show_rooms: bool = True  # Add show_rooms parameter with default True
):
    """
    Endpoint to get hotel data in multiple languages and optionally include room and photo data for multiple hotels.

    Args:
        expire_hours: Expiration time for caching data.
        hotel_ids (List[int]): A list of hotel IDs (default to [4469654]).
        redis (Redis): The Redis client instance.
        show_photos (bool): Whether to fetch and include photos. Defaults to True.
        show_rooms (bool): Whether to fetch and include room data. Defaults to True.

    Returns:
        List[DetailedHotelResponse]: The transformed JSON response containing hotel data for each hotel in multiple languages and room data.
    """
    languages = ['it', 'en-gb', 'es', 'fr', 'de']
    detailed_hotels = []

    # Loop over each hotel_id and fetch the data
    for hotel_id in hotel_ids:
        cache_key_template = f"hotel_data_{{}}_{hotel_id}"

        # Initialize the transformed_data structure based on the Pydantic model
        transformed_data = {
            "items": {
                "hotel": {
                    "hotel_id": hotel_id,
                    "name": "",
                    "country": {lang: "" for lang in languages},
                    "country_id": 1,
                    "city": {lang: "" for lang in languages},
                    "city_id": 1,
                    "district": {lang: "" for lang in languages},
                    "district_id": 1,
                    "photos": [],  # Photos will be added here if show_photos is True
                    "location": {"latitude": 0, "longitude": 0},
                    "zip": "",
                    "address": "",
                    "checkin": {"from": "00:00", "to": "00:00"},
                    "checkout": {"from": "00:00", "to": "00:00"},
                    "stars": 1,
                    "facilities": {lang: [] for lang in languages},
                    "number_of_rooms": 1,
                    "description": {lang: "" for lang in languages},
                    "rooms": []  # Rooms will be added here if show_rooms is True
                }
            }
        }

        # Fetch and transform data for each language
        for lang in languages:
            params = {'hotel_id': hotel_id, 'locale': lang}
            cache_key = cache_key_template.format(lang)

            # Fetch hotel data for the current language
            raw_data = await get_data_or_cache("data", params, cache_key, redis_expire_seconds, redis, expire_hours)

            # Use the transformation function to convert raw data and store results per language
            lang_transformed_data = await transform_data(raw_data)

            # Store transformed results for each language in the appropriate fields
            transformed_data["items"]["hotel"]["name"] = lang_transformed_data["items"]["hotel"]["name"]
            transformed_data["items"]["hotel"]["location"] = lang_transformed_data["items"]["hotel"]["location"]
            transformed_data["items"]["hotel"]["country"][lang] = lang_transformed_data["items"]["hotel"]["country"][
                "en"]
            transformed_data["items"]["hotel"]["city"][lang] = lang_transformed_data["items"]["hotel"]["city"]["en"]
            transformed_data["items"]["hotel"]["zip"] = lang_transformed_data["items"]["hotel"]["zip"]
            transformed_data["items"]["hotel"]["district_id"] = lang_transformed_data["items"]["hotel"]["district_id"]
            transformed_data["items"]["hotel"]["district"][lang] = lang_transformed_data["items"]["hotel"]["district"][
                "en"]
            transformed_data["items"]["hotel"]["description"][lang] = \
                lang_transformed_data["items"]["hotel"]["description"][lang]
            transformed_data["items"]["hotel"]["address"] = lang_transformed_data["items"]["hotel"]["address"]
            transformed_data["items"]["hotel"]["checkin"] = lang_transformed_data["items"]["hotel"]["checkin"]
            transformed_data["items"]["hotel"]["checkout"] = lang_transformed_data["items"]["hotel"]["checkout"]
            transformed_data["items"]["hotel"]["stars"] = lang_transformed_data["items"]["hotel"]["stars"]
            transformed_data["items"]["hotel"]["number_of_rooms"] = lang_transformed_data["items"]["hotel"][
                "number_of_rooms"]
            transformed_data["items"]["hotel"]["facilities"][lang] = \
                lang_transformed_data["items"]["hotel"]["facilities"]["en"]
            transformed_data["items"]["hotel"]["review_score"] = lang_transformed_data["items"]["hotel"]["review_score"]
            transformed_data["items"]["hotel"]["review_nr"] = lang_transformed_data["items"]["hotel"]["review_nr"]
            transformed_data["items"]["hotel"]["review_score_word"] = lang_transformed_data["items"]["hotel"][
                "review_score_word"]
            transformed_data["items"]["hotel"]["entrance_photo_url"] = lang_transformed_data["items"]["hotel"][
                "entrance_photo_url"]
            transformed_data["items"]["hotel"]["main_photo_url"] = lang_transformed_data["items"]["hotel"][
                "main_photo_url"]

        # Optionally fetch photos once for 'en-gb' only if show_photos is True
        if show_photos:
            photo_params = {'hotel_id': hotel_id, 'locale': 'en-gb'}
            photo_cache_key = f"hotel_photos_{hotel_id}_en-gb"
            photo_data = await get_data_or_cache("photos", photo_params, photo_cache_key, redis_expire_seconds, redis,
                                                 expire_hours)

            if photo_data:
                transformed_data["items"]["hotel"]["photos"] = photo_data

        # Optionally fetch room data if show_rooms is True
        if show_rooms:
            room_data = await get_hotel_room_list(
                hotel_id=hotel_id,
                redis=redis,
                expire_hours=expire_hours
            )

            if room_data:
                transformed_room_data = await transform_room_data(room_data)
                transformed_data["items"]["hotel"]["rooms"] = transformed_room_data["rooms"]

        # Append the transformed hotel data to the list
        detailed_hotels.append(DetailedHotelResponse(**transformed_data))

    # Return the list of transformed data for each hotel
    return detailed_hotels
