from typing import Optional, Dict, Any
from pydantic import BaseModel


class Location(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class Checkin(BaseModel):
    from_time: Optional[str] = None
    to: Optional[str] = None


class Checkout(BaseModel):
    from_time: Optional[str] = None
    to: Optional[str] = None


class Hotel(BaseModel):
    hotel_id: Optional[int] = None
    name: Optional[str] = None
    country: Optional[Dict[str, Optional[str]]] = None  # Language-specific country names
    country_id: Optional[int] = None
    city: Optional[Dict[str, Optional[str]]] = None  # Language-specific city names
    city_id: Optional[int] = None
    district: Optional[Dict[str, Optional[str]]] = None  # Language-specific district names
    district_id: Optional[int] = None
    photos: Optional[list] = None  # Default to empty dict
    location: Optional[Location] = Location()  # Default to empty Location object
    zip: Optional[str] = None
    address: Optional[str] = None
    checkin: Optional[Checkin] = Checkin()  # Default to empty Checkin object
    checkout: Optional[Checkout] = Checkout()  # Default to empty Checkout object
    stars: Optional[int] = None
    number_of_rooms: Optional[int] = None
    description: Optional[Dict[str, Optional[str]]] = {}  # Default to empty dict
    rooms: Optional[Any] = []  # Default to empty list
    review_score: Optional[str] = None
    review_nr: Optional[int] = None
    review_score_word: Optional[str] = None
    entrance_photo_url: Optional[str] = None
    main_photo_url: Optional[str] = None
    facilities: Optional[Any] = {}  # Default to empty dict


class Items(BaseModel):
    hotel: Optional[Hotel] = Hotel()  # Default to empty Hotel object


class DetailedHotelResponse(BaseModel):
    items: Optional[Items] = Items()  # Default to empty Items object
