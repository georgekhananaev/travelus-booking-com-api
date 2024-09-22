from typing import List, Optional
from pydantic import BaseModel, Field


class Location(BaseModel):
    longitude: Optional[float] = None
    latitude: Optional[float] = None


class DescriptionTranslation(BaseModel):
    description: Optional[str] = None
    languagecode: Optional[str] = None
    descriptiontype_id: Optional[int] = None


class CheckinCheckout(BaseModel):
    to: Optional[str] = None
    from_: Optional[str] = Field(None, alias='from')
    hour_available_24: Optional[int] = Field(None, alias='24_hour_available')  # Correct alias


class BookingHome(BaseModel):
    group: Optional[str] = None
    is_aparthotel: Optional[int] = None
    is_single_type_property: Optional[int] = None
    is_booking_home: Optional[int] = None
    is_vacation_rental: Optional[int] = None
    quality_class: Optional[int] = None
    is_single_unit_property: Optional[int] = None
    segment: Optional[int] = None


class Hotel(BaseModel):
    hotel_id: Optional[int] = None
    name: Optional[str] = None
    description_translations: Optional[List[DescriptionTranslation]] = None
    class_: Optional[int] = Field(None, alias='class')
    location: Optional[Location] = None
    city_id: Optional[int] = None
    main_photo_url: Optional[str] = None
    zip: Optional[str] = None
    is_single_unit_vr: Optional[int] = None
    district: Optional[str] = None
    ranking: Optional[int] = None
    district_id: Optional[int] = None
    class_is_estimated: Optional[int] = None
    checkout: Optional[CheckinCheckout] = None
    preferred: Optional[int] = None
    preferred_plus: Optional[int] = None
    main_photo_id: Optional[int] = None
    hoteltype_id: Optional[int] = None
    languages_spoken: Optional[dict] = None
    hotel_facilities: Optional[str] = None
    review_nr: Optional[int] = None
    review_score: Optional[str] = None
    review_score_word: Optional[str] = None
    currencycode: Optional[str] = None
    entrance_photo_url: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    url: Optional[str] = None
    checkin: Optional[CheckinCheckout] = None
    hotel_facilities_filtered: Optional[str] = None
    countrycode: Optional[str] = None
    is_vacation_rental: Optional[int] = None
    booking_home: Optional[BookingHome] = None


class HotelsResponse(BaseModel):
    hotels: List[Hotel]
