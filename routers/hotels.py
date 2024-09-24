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
from components.transform_data import transform_data, transform_room_data, extract_hotel_data
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
        hotel_id: int = Query(default=4469654, description="The unique ID of the hotel for which details are being requested. Default is 4469654."),
        locale: str = Query(default="en-gb", description="The locale for language and formatting preferences. Default is 'en-gb'."),
        redis: Redis = Depends(AsyncRedisClient.get_instance),  # Redis dependency for caching
        expire_hours: int = Query(default=mongo_expire_hours, description="The number of hours for which the hotel data will be cached. Uses a default value defined by mongo_expire_hours.")
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
        hotel_ids: List[int] = Query(default=[2534439, 4469654], alias="hotel_ids", description="A list of hotel IDs to fetch information for. Default values are 2534439 and 4469654."),
        locale: str = Query(default="en-gb", description="The locale for language and formatting preferences. Default is 'en-gb'."),
        redis: Redis = Depends(AsyncRedisClient.get_instance),  # Redis dependency for caching
        expire_hours: int = Query(default=72, description="The number of hours for which the data will be cached. Default is 72 hours.")
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
        req: Request,  # Request object for metadata and context
        hotel_id: int = Query(default=4469654, description="The ID of the hotel to fetch details for. Default is 4469654."),
        locale: str = Query(default="en-gb", description="The locale for language and formatting preferences. Default is 'en-gb'."),
        expire_hours: int = Query(default=mongo_expire_hours, description="The number of hours for which the data will be cached. The default value is taken from the environment setting (mongo_expire_hours).")
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
        hotel_id: int = Query(default=4469654, description="The ID of the hotel to fetch reviews for. Default is 4469654."),
        locale: str = Query(default="en-gb", description="The locale for language and formatting preferences. Default is 'en-gb'."),
        customer_type: str = Query(default="solo_traveller,review_category_group_of_friends", description="Filter reviews by customer types. Provide customer types separated by commas. For example: 'solo_traveller,review_category_group_of_friends'."),
        sort_type: str = Query(default="SORT_MOST_RELEVANT", description="The sort type for the reviews. Default is 'SORT_MOST_RELEVANT'."),
        language_filter: str = Query(default="en-us", description="Filter reviews by language. Default is 'en-us'."),
        page_number: int = Query(default=0, description="The page number for pagination. Default is 0 (first page)."),
        redis: Redis = Depends(AsyncRedisClient.get_instance),  # Redis instance for caching
        expire_hours: int = Query(default=mongo_expire_hours, description="The number of hours for which the data will be cached. The default value is taken from the environment setting (mongo_expire_hours).")
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
        hotel_id: int = Query(default=4469654, description="The ID of the hotel to fetch room data for. Default is 4469654."),
        checkin_date: str = Query(default=(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'), description="Check-in date in YYYY-MM-DD format. Default is 30 days from today."),
        checkout_date: str = Query(default=(datetime.now() + timedelta(days=31)).strftime('%Y-%m-%d'), description="Check-out date in YYYY-MM-DD format. Default is 31 days from today."),
        children_ages: Optional[str] = Query(
            default=None,
            description="(Optional) The age of each child. Indicate their ages separated by commas. For example, '0,5' means one child is under 1 year old and another is 5 years old."
        ),
        children_number_by_rooms: Optional[str] = Query(
            default=None,
            description="(Optional) The number of children in each room. Specify the number of children separated by commas. For example, '2,1' means the first room will have 2 children, and the second room will have 1 child."
        ),
        adults_number_by_rooms: str = Query(
            default="2,1",
            description="The number of adults in each room. Specify the number of adults separated by commas. For example, '3,1' means the first room will have 3 adults, and the second room will have 1 adult. To book a single room for 2 adults, specify '2'."
        ),
        units: str = Query(default="metric", description="The unit system to use for room measurements. Default is 'metric'."),
        currency: str = Query(default="EUR", description="The currency to display prices in. Default is 'EUR' (Thai Baht)."),
        locale: str = Query(default="en-gb", description="The locale for language and formatting preferences. Default is 'en-gb'."),
        redis: Redis = Depends(AsyncRedisClient.get_instance),  # Redis instance for caching
        expire_hours: int = Query(default=8, description="The number of hours for which the data will be cached. Default is 8 hours.")
):
    # Build params dictionary without children if they are None, empty, or zero
    params = {
        'hotel_id': hotel_id,
        'checkin_date': checkin_date,
        'checkout_date': checkout_date,
        'adults_number_by_rooms': adults_number_by_rooms,
        'units': units,
        'currency': currency,
        'locale': locale
    }

    # Add children parameters only if they are not None, empty, or zero
    if children_ages and children_ages != "0":
        params['children_ages'] = children_ages
    if children_number_by_rooms and children_number_by_rooms != "0":
        params['children_number_by_rooms'] = children_number_by_rooms

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


# Endpoint to get combined hotel data
@router.get("/room-min-price-list")
async def get_combined_hotel_data(
        hotel_ids: List[int] = Query(
            default=[46748, 176457],
            alias="hotel_ids",
            description="A list of hotel IDs to retrieve data for. Specify multiple hotel IDs separated by commas."
        ),
        locale: str = Query(
            default="en-gb",
            description="The locale or language to use for the data, e.g., 'en-gb' for English (UK)."
        ),
        checkin_date: str = Query(
            default=(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            description="Check-in date in the format YYYY-MM-DD. Defaults to 30 days from today."
        ),
        checkout_date: str = Query(
            default=(datetime.now() + timedelta(days=31)).strftime('%Y-%m-%d'),
            description="Checkout date in the format YYYY-MM-DD. Defaults to 31 days from today."
        ),
        adults_number_by_rooms: Optional[str] = Query(
            default="2,1",
            description="A comma-separated list of the number of adults per room. E.g., '2,1' means 2 adults in the first room and 1 adult in the second."
        ),
        children_number_by_rooms: Optional[str] = Query(
            default=None,
            description="(Optional) A comma-separated list of the number of children per room. E.g., '2,1' means 2 children in the first room and 1 child in the second."
        ),
        children_ages: Optional[str] = Query(
            default=None,
            description="(Optional) A comma-separated list of children's ages. E.g., '0,5' for a 0-year-old and a 5-year-old."
        ),
        available_rooms_only: bool = Query(
            default=False,
            description="Set this to 'True' to display only available rooms. If set to 'False,' it will show the lowest price in the system, including unavailable rooms. If min_price is 0, it means no rooms were found."
        ),
        redis: Redis = Depends(AsyncRedisClient.get_instance),  # Redis client
        expire_hours: int = Query(
            default=48,
            description="The cache expiry time in hours. The data will be cached for this amount of time."
        )
):
    # Step 1: Extract the values from the Query objects and form the correct parameters for use in the database
    params = {
        'hotel_ids': hotel_ids,
        'locale': locale,
        'currency': "metric",
        'checkin_date': checkin_date,
        'checkout_date': checkout_date,
        'units': "EUR",
        'adults_number_by_rooms': adults_number_by_rooms,
    }

    # Only add children-related fields if provided
    if children_number_by_rooms:
        params['children_number_by_rooms'] = children_number_by_rooms
    if children_ages:
        params['children_ages'] = children_ages

    # Step 2: Fetch hotel and room data concurrently
    hotel_data_tasks = [
        get_hotel_data(hotel_id=hotel_id, locale=locale, redis=redis, expire_hours=expire_hours)
        for hotel_id in hotel_ids
    ]
    room_data_tasks = [
        get_hotel_room_list(hotel_id=hotel_id, checkin_date=checkin_date, checkout_date=checkout_date,
                            units="metric", currency="EUR", locale=locale, redis=redis, expire_hours=expire_hours,
                            adults_number_by_rooms=adults_number_by_rooms,
                            children_number_by_rooms=children_number_by_rooms,
                            children_ages=children_ages)
        for hotel_id in hotel_ids
    ]

    # Step 3: Run both hotel and room tasks concurrently
    hotel_responses = await asyncio.gather(*hotel_data_tasks)
    room_responses = await asyncio.gather(*room_data_tasks)

    # Step 4: Combine hotel and room data
    combined_data = []
    for hotel_response, room_response in zip(hotel_responses, room_responses):
        hotel_dict = hotel_response.dict()
        room_list = [room.dict() for room in room_response] if room_response else []
        hotel_data = await extract_hotel_data(hotel_dict, room_list, available_rooms_only)
        combined_data.append(hotel_data)

    return combined_data


@router.get("/detailed_hotel", response_model=List[DetailedHotelResponse])
async def mock_detail_hotel(
        hotel_ids: List[int] = Query(default=[4469654], description="A list of hotel IDs to fetch the information for. Example: [4469654, 1234567]."),
        redis: Redis = Depends(AsyncRedisClient.get_instance),  # Redis instance dependency for caching
        expire_hours: int = Query(default=72, description="The number of hours for which the data is cached. Default is 72 hours."),
        disable_google_translations: bool = Query(default=True, description="If set to True, Google Translations are disabled. Default is True."),
        show_photos: bool = Query(default=True, description="If set to True, the hotel photos will be included in the response. Default is True."),
        show_rooms: bool = Query(default=False, description="If set to True, room information will be included in the response. Default is False.")
):
    """
    Endpoint to get hotel data in multiple languages and optionally include room and photo data for multiple hotels.

    Args:
        disable_google_translations:
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
                transformed_room_data = await transform_room_data(room_data, disable_google_translations)
                transformed_data["items"]["hotel"]["rooms"] = transformed_room_data["rooms"]

        # Append the transformed hotel data to the list
        detailed_hotels.append(DetailedHotelResponse(**transformed_data))

    # Return the list of transformed data for each hotel
    return detailed_hotels
