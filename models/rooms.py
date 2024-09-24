from typing import Optional, List, Dict, Union, Any
from pydantic import BaseModel, validator # noqa


class BMaxLosData(BaseModel):
    is_fullon: Optional[int] = None
    extended_los: Optional[int] = None
    max_allowed_los: Optional[int] = None
    experiment: Optional[str] = None
    has_extended_los: Optional[int] = None
    default_los: Optional[int] = None


class Facility(BaseModel):
    facilitytype_id: Optional[int] = None
    id: Optional[int] = None
    name: Optional[str] = None
    alt_facilitytype_id: Optional[int] = None
    alt_facilitytype_name: Optional[str] = None


class Highlight(BaseModel):
    translated_name: Optional[str] = None
    icon: Optional[str] = None
    id: Optional[Union[str, int]] = None  # Make this field optional


class BedType(BaseModel):
    name_with_count: Optional[str] = None
    count: Optional[int] = None
    description_localized: Optional[str] = None  # Optional field
    description_imperial: Optional[str] = None
    name: Optional[str] = None
    bed_type: Optional[int] = None
    description: Optional[str] = None


class BedConfiguration(BaseModel):
    bed_types: Optional[List[BedType]] = None


class Photo(BaseModel):
    photo_id: Optional[Union[str, int]] = None  # Allow either string or integer
    ratio: Optional[Union[str, float]] = None  # Allow either string or float
    new_order: Optional[Union[str, int]] = None  # Allow either string or integer


class Room(BaseModel):
    facilities: Optional[List[Facility]] = None
    description: Optional[str] = None
    highlights: Optional[List[Highlight]]  # Optional highlights list
    bed_configurations: Optional[List[BedConfiguration]] = None
    private_bathroom_count: Optional[int] = None
    children_and_beds_text: Optional[Dict] = None
    is_high_floor_guaranteed: Optional[int] = None
    private_bathroom_highlight: Optional[Dict] = None
    photos: Optional[List[Photo]] = None


class MinRoomDistribution(BaseModel):
    children: Optional[List[int]] = None
    adults: Optional[int] = None


class RoomRecommendation(BaseModel):
    total_extra_bed_price: Optional[int] = None
    children: Optional[int] = None
    block_id: Optional[str] = None
    number_of_extra_beds: Optional[int] = None
    babies: Optional[int] = None
    adults: Optional[int] = None
    total_extra_bed_price_in_hotel_currency: Optional[int] = None


class RoomsData(BaseModel):
    block: Optional[Any] = []
    b_max_los_data: Optional[BMaxLosData] = None
    rooms: Optional[Any] = []
    preferences: Optional[List[str]] = []
    recommended_block_title: Optional[str] = None
    hotel_id: Optional[int]
    qualifies_for_no_cc_reservation: Optional[int] = None
    address_required: Optional[int] = None
    min_room_distribution: Optional[MinRoomDistribution] = None
    cvc_required: Optional[str] = None
    is_cpv2_property: Optional[int] = None
    cheapest_avail_price_eur: Optional[float] = None
    room_recommendation: Optional[List[RoomRecommendation]] = []
    currency_code: Optional[str] = None
    b_blackout_android_prepayment_copy: Optional[int] = None
    departure_date: Optional[str] = None
    arrival_date: Optional[str] = None
    prepayment_policies: Optional[Any] = None
    direct_payment: Optional[Any] = None
    cancellation_policies: Optional[Any] = None
    cc_required: Optional[str] = None
    payment_detail: Optional[Any] = None
    max_rooms_in_reservation: Optional[int] = None
    is_exclusive: Optional[int] = None
    total_blocks: Optional[int] = None
    duplicate_rates_removed: Optional[int] = None
    top_ufi_benefits: Optional[Any] = None
    last_matching_block_index: Optional[int] = None
    soldout_rooms: Optional[List[str]] = []
    tax_exceptions: Optional[List[str]] = []
    preferences: Optional[Any] = None

    # Validator for the 'preferences' field
    @validator("preferences", pre=True, always=True) # noqa
    def validate_preferences(cls, v):
        # Ensure that 'preferences' is a list of strings or valid data
        if isinstance(v, list):
            # Keep only string preferences, ignore others
            return [item if isinstance(item, str) else str(item) for item in v]
        return []

    class Config:
        extra = 'ignore'
