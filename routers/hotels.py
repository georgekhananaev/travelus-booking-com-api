from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from redis.asyncio import Redis
from db.redis_client import AsyncRedisClient
from db.rapidapi_client import get_data_or_cache

router = APIRouter()


# 1. Endpoint to get hotel photos
@router.get("/photos")
async def get_hotel_photos(hotel_id: int = 4469654, locale: str = "en-gb",
                           redis: Redis = Depends(AsyncRedisClient.get_instance)):
    params = {'hotel_id': hotel_id, 'locale': locale}
    cache_key = f"hotel_photos_{hotel_id}_{locale}"
    expire_seconds = int(timedelta(seconds=5).total_seconds())

    return await get_data_or_cache("photos", params, cache_key, expire_seconds, redis)


# 2. Endpoint to get hotel data
@router.get("/data")
async def get_hotel_data(hotel_id: int = 4469654, locale: str = "en-gb",
                         redis: Redis = Depends(AsyncRedisClient.get_instance)):
    params = {'hotel_id': hotel_id, 'locale': locale}
    cache_key = f"hotel_data_{hotel_id}_{locale}"
    expire_seconds = int(timedelta(seconds=5).total_seconds())

    return await get_data_or_cache("data", params, cache_key, expire_seconds, redis)


# 3. Endpoint to get hotel reviews
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
    params = {
        'hotel_id': hotel_id,
        'locale': locale,
        'customer_type': customer_type,
        'sort_type': sort_type,
        'language_filter': language_filter,
        'page_number': page_number
    }
    cache_key = f"hotel_reviews_{hotel_id}_{locale}_{customer_type}_{sort_type}_{language_filter}_{page_number}"
    expire_seconds = int(timedelta(hours=24).total_seconds())

    return await get_data_or_cache("reviews", params, cache_key, expire_seconds, redis)


# 4. Endpoint to get hotel room list
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
    expire_seconds = int(timedelta(hours=8).total_seconds())

    return await get_data_or_cache("room-list", params, cache_key, expire_seconds, redis)
