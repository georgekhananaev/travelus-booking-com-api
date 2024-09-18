from fastapi import APIRouter, Depends
from datetime import timedelta
from redis.asyncio import Redis

from db.redis_client import AsyncRedisClient
from components.facilities import map_facility_ids, facilities
from components.transform_data import transform_data, transform_room_data
from routers.hotels import get_data_or_cache, get_hotel_room_list

router = APIRouter()


@router.get("/hotel_data")
async def mock_detail_hotel(hotel_id: int = 4469654, redis: Redis = Depends(AsyncRedisClient.get_instance)):
    """
    Endpoint to get hotel data in multiple languages and include room data.

    Args:
        hotel_id (int): The ID of the hotel.
        redis (Redis): The Redis client instance.

    Returns:
        dict: The transformed JSON response containing hotel data in multiple languages and room data.
    """
    # Define the list of valid languages to fetch data for
    languages = ['it', 'en-gb', 'es', 'fr', 'de']

    # Define a cache key template
    cache_key_template = f"hotel_data_{{}}_{hotel_id}"

    # Initialize a dictionary to store transformed data for each language
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
                "photos": {},  # Photos will be added here in "en-gb"
                "location": {"latitude": 0, "longitude": 0},
                "zip": "",
                "address": "",
                "checkin": {"from": "00:00", "to": "00:00"},
                "checkout": {"from": "00:00", "to": "00:00"},
                "stars": 1,
                "facilities": {lang: [] for lang in languages},  # Facilities are language-specific
                "number_of_rooms": 1,
                "description": {lang: "" for lang in languages},
                "rooms": []  # Rooms don't need language translation, so using a list
            }
        }
    }

    # Fetch and transform data for each language
    for lang in languages:
        params = {'hotel_id': hotel_id, 'locale': lang}
        cache_key = cache_key_template.format(lang)

        # Fetch data from cache or API for the current language
        raw_data = await get_data_or_cache("data", params, cache_key,
                                           int(timedelta(hours=24).total_seconds()), redis)

        # Use the transformation function to convert raw data and store results per language
        lang_transformed_data = transform_data(raw_data)

        # Store transformed results for each language in the appropriate fields
        transformed_data["items"]["hotel"]["name"] = lang_transformed_data["items"]["hotel"]["name"]
        transformed_data["items"]["hotel"]["location"] = lang_transformed_data["items"]["hotel"]["location"]
        transformed_data["items"]["hotel"]["country"][lang] = lang_transformed_data["items"]["hotel"]["country"]["en"]
        transformed_data["items"]["hotel"]["city"][lang] = lang_transformed_data["items"]["hotel"]["city"]["en"]
        transformed_data["items"]["hotel"]["zip"] = lang_transformed_data["items"]["hotel"]["zip"]
        transformed_data["items"]["hotel"]["district_id"] = lang_transformed_data["items"]["hotel"]["district_id"]
        transformed_data["items"]["hotel"]["district"][lang] = lang_transformed_data["items"]["hotel"]["district"]["en"]
        transformed_data["items"]["hotel"]["description"][lang] = \
            lang_transformed_data["items"]["hotel"]["description"]["en"]
        transformed_data["items"]["hotel"]["address"] = lang_transformed_data["items"]["hotel"]["address"]
        transformed_data["items"]["hotel"]["checkin"] = lang_transformed_data["items"]["hotel"]["checkin"]
        transformed_data["items"]["hotel"]["checkout"] = lang_transformed_data["items"]["hotel"]["checkout"]
        transformed_data["items"]["hotel"]["stars"] = lang_transformed_data["items"]["hotel"]["stars"]
        transformed_data["items"]["hotel"]["number_of_rooms"] = lang_transformed_data["items"]["hotel"][
            "number_of_rooms"]
        transformed_data["items"]["hotel"]["facilities"][lang] = lang_transformed_data["items"]["hotel"]["facilities"][
            "en"]
        transformed_data["items"]["hotel"]["review_score"] = lang_transformed_data["items"]["hotel"]["review_score"]
        transformed_data["items"]["hotel"]["review_nr"] = lang_transformed_data["items"]["hotel"]["review_nr"]
        transformed_data["items"]["hotel"]["review_score_word"] = lang_transformed_data["items"]["hotel"][
            "review_score_word"]
        transformed_data["items"]["hotel"]["entrance_photo_url"] = lang_transformed_data["items"]["hotel"][
            "entrance_photo_url"]
        transformed_data["items"]["hotel"]["main_photo_url"] = lang_transformed_data["items"]["hotel"]["main_photo_url"]

        # Parse facilities for each language and map them to names
        if "hotel_facilities" in raw_data:
            facilities_list_ids = list(map(int, raw_data["hotel_facilities"].split(',')))
            facilities_names = map_facility_ids(facilities_list_ids, facilities, lang)
            transformed_data["items"]["hotel"]["facilities"][lang] = facilities_names

    # Fetch photos once for 'en-gb' only
    photo_params = {'hotel_id': hotel_id, 'locale': 'en-gb'}
    photo_cache_key = f"hotel_photos_{hotel_id}_en-gb"

    # Fetch photos from cache or API
    photo_data = await get_data_or_cache("photos", photo_params, photo_cache_key,
                                         int(timedelta(hours=24).total_seconds()), redis)

    # Add photos to the response (assuming the structure of the returned photo data is a list)
    if photo_data:
        transformed_data["items"]["hotel"]["photos"] = photo_data

    # Fetch room data separately using get_hotel_room_list
    room_data = await get_hotel_room_list(
        hotel_id=hotel_id,
        redis=redis  # Pass the Redis client instance
    )

    # Transform room data using transform_room_data
    if room_data:
        transformed_room_data = transform_room_data(room_data)
        transformed_data["items"]["hotel"]["rooms"] = transformed_room_data["rooms"]

    return transformed_data