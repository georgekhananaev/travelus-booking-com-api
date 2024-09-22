from typing import Optional, List, Dict, Union, Any
from pydantic import BaseModel


class BMaxLosData(BaseModel):
    is_fullon: Optional[int]
    extended_los: Optional[int]
    max_allowed_los: Optional[int]
    experiment: Optional[str]
    has_extended_los: Optional[int]
    default_los: Optional[int]


class Facility(BaseModel):
    facilitytype_id: Optional[int]
    id: Optional[int]
    name: Optional[str]
    alt_facilitytype_id: Optional[int]
    alt_facilitytype_name: Optional[str]


class Highlight(BaseModel):
    translated_name: Optional[str]
    icon: Optional[str]
    id: Optional[Union[str, int]]  # Make this field optional


class BedType(BaseModel):
    name_with_count: Optional[str]
    count: Optional[int]
    description_localized: Optional[str]  # Optional field
    description_imperial: Optional[str]
    name: Optional[str]
    bed_type: Optional[int]
    description: Optional[str]


class BedConfiguration(BaseModel):
    bed_types: Optional[List[BedType]]


class Photo(BaseModel):
    photo_id: Optional[Union[str, int]]  # Allow either string or integer
    ratio: Optional[Union[str, float]]  # Allow either string or float
    new_order: Optional[Union[str, int]]  # Allow either string or integer


class Room(BaseModel):
    facilities: Optional[List[Facility]]
    description: Optional[str]
    highlights: Optional[List[Highlight]]  # Optional highlights list
    bed_configurations: Optional[List[BedConfiguration]]
    private_bathroom_count: Optional[int]
    children_and_beds_text: Optional[Dict]
    is_high_floor_guaranteed: Optional[int]
    private_bathroom_highlight: Optional[Dict]
    photos: Optional[List[Photo]]


class MinRoomDistribution(BaseModel):
    children: Optional[List[int]]
    adults: Optional[int]


class RoomRecommendation(BaseModel):
    total_extra_bed_price: Optional[int]
    children: Optional[int]
    block_id: Optional[str]
    number_of_extra_beds: Optional[int]
    babies: Optional[int]
    adults: Optional[int]
    total_extra_bed_price_in_hotel_currency: Optional[int]


class RoomsData(BaseModel):
    block: Optional[Any] = []
    b_max_los_data: Optional[BMaxLosData]
    rooms: Optional[Any] = []
    preferences: Optional[List[str]]
    recommended_block_title: Optional[str]
    hotel_id: Optional[int]
    qualifies_for_no_cc_reservation: Optional[int]
    address_required: Optional[int]
    min_room_distribution: Optional[MinRoomDistribution]
    cvc_required: Optional[str]
    is_cpv2_property: Optional[int]
    cheapest_avail_price_eur: Optional[float]
    room_recommendation: Optional[List[RoomRecommendation]]
    currency_code: Optional[str]
    b_blackout_android_prepayment_copy: Optional[int]
    departure_date: Optional[str]
    arrival_date: Optional[str]
    prepayment_policies: Optional[Dict[str, Optional[str]]]
    direct_payment: Optional[Dict[str, Optional[int]]]
    cancellation_policies: Optional[Dict[str, Optional[str]]]
    cc_required: Optional[str]
    payment_detail: Optional[Dict[str, Optional[str]]]
    max_rooms_in_reservation: Optional[int]
    is_exclusive: Optional[int]
    total_blocks: Optional[int]
    duplicate_rates_removed: Optional[int]
    top_ufi_benefits: Optional[List[Dict[str, Optional[str]]]]
    last_matching_block_index: Optional[int]
    soldout_rooms: Optional[List[str]]
    tax_exceptions: Optional[List[str]]

    class Config:
        extra = 'ignore'  # This will ignore any additional fields not defined in the model
