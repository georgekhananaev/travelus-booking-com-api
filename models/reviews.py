from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime


class Photo(BaseModel):
    photo_id: Optional[int] = None
    url_max300: Optional[HttpUrl] = None
    url_640x200: Optional[HttpUrl] = None
    url_square60: Optional[HttpUrl] = None
    url_original: Optional[HttpUrl] = None
    ratio: Optional[float] = None


class StayedRoomInfo(BaseModel):
    room_id: Optional[int] = None
    room_name: Optional[str] = None
    num_nights: Optional[int] = None
    checkin: Optional[datetime] = None
    checkout: Optional[datetime] = None
    photo: Optional[Photo] = None


class Author(BaseModel):
    name: Optional[str] = None
    user_id: Optional[int] = None
    countrycode: Optional[str] = None
    nr_reviews: Optional[int] = None
    type: Optional[str] = None
    type_string: Optional[str] = None
    city: Optional[str] = None
    avatar: Optional[HttpUrl] = None
    helpful_vote_count: Optional[int] = None


class Review(BaseModel):
    review_id: Optional[int] = None
    hotel_id: Optional[int] = None
    date: Optional[datetime] = None
    languagecode: Optional[str] = None
    title: Optional[str] = None
    pros: Optional[str] = None
    cons: Optional[str] = None
    travel_purpose: Optional[str] = None
    average_score: Optional[float] = None
    stayed_room_info: Optional[StayedRoomInfo] = None
    author: Optional[Author] = None
    helpful_vote_count: Optional[int] = None
    hotelier_name: Optional[str] = None
    hotelier_response: Optional[str] = None
    hotelier_response_date: Optional[int] = None
    reviewer_photos: Optional[List[Photo]] = None
    tags: Optional[List[str]] = None


class ReviewsResponse(BaseModel):
    result: Optional[List[Review]] = None
    count: Optional[int] = None
    sort_options: Optional[List[str]] = None
