import asyncio
import json
from typing import List, Dict, Union

from components.translator import async_translate
from models.rooms import RoomsData
from components.facilities import map_facility_ids, facilities


async def transform_data(input_data):
    """
    Asynchronously transforms the input data to return the hotel data with facilities and other relevant information.

    Args:
    input_data: The raw hotel data that needs to be transformed.

    Returns:
    dict: Transformed hotel data with facilities mapped to their names.
    """
    languages = ['it', 'en', 'es', 'fr', 'de']

    # Fetch facility IDs from the input data
    facility_ids = list(
        map(int, input_data.get("hotel_facilities", "").split(','))) if "hotel_facilities" in input_data else []

    # Create facilities mapping for each language using map_facility_ids
    # Assuming map_facility_ids is an async function
    facilities_transformed = {
        lang: map_facility_ids(facility_ids, facilities, lang) for lang in languages
    }

    return {
        "items": {
            "hotel": {
                "hotel_id": input_data.get("hotel_id", 1),
                "name": input_data.get("name", ""),
                "country": {
                    "it": "",
                    "en": input_data.get("country", ""),
                    "es": "",
                    "fr": "",
                    "de": ""
                },
                "country_id": input_data.get("country_id", 1),
                "city": {
                    "it": "",
                    "en": input_data.get("city", ""),
                    "es": "",
                    "fr": "",
                    "de": ""
                },
                "city_id": input_data.get("city_id", 1),
                "district": {
                    "it": input_data.get("district", ""),
                    "en": input_data.get("district", ""),
                    "es": input_data.get("district", ""),
                    "fr": input_data.get("district", ""),
                    "de": input_data.get("district", "")
                },
                "district_id": input_data.get("district_id", 1),
                "location": {
                    "latitude": input_data.get("location", {}).get("latitude", 0),
                    "longitude": input_data.get("location", {}).get("longitude", 0)
                },
                "zip": input_data.get("zip", ""),
                "address": input_data.get("address", ""),
                "checkin": {
                    "from": input_data.get("checkin", {}).get("from", "00:00"),
                    "to": input_data.get("checkin", {}).get("to", "00:00")
                },
                "checkout": {
                    "from": input_data.get("checkout", {}).get("from", "00:00"),
                    "to": input_data.get("checkout", {}).get("to", "00:00")
                },
                "stars": input_data.get("class", 1),
                "review_score": input_data.get("review_score", 0),
                "review_nr": input_data.get("review_nr", 0),
                "review_score_word": input_data.get("review_score_word", ""),
                "facilities": facilities_transformed,  # Map facilities for each language
                "number_of_rooms": 1,
                "description": {
                    "it": next((d["description"] for d in input_data.get("description_translations", []) if
                                d.get("languagecode") == "it"), ""),
                    "en": next((d["description"] for d in input_data.get("description_translations", []) if
                                d.get("languagecode") == "en-gb"), ""),
                    "en-gb": next((d["description"] for d in input_data.get("description_translations", []) if
                                   d.get("languagecode") == "en-gb"), ""),
                    "es": next((d["description"] for d in input_data.get("description_translations", []) if
                                d.get("languagecode") == "es"), ""),
                    "fr": next((d["description"] for d in input_data.get("description_translations", []) if
                                d.get("languagecode") == "fr"), ""),
                    "de": next((d["description"] for d in input_data.get("description_translations", []) if
                                d.get("languagecode") == "de"), "")
                },
                "main_photo_url": input_data.get("main_photo_url", ""),
                "entrance_photo_url": input_data.get("entrance_photo_url", ""),
                "rooms": [
                    {
                        "hotel_id": input_data.get("hotel_id", 1),
                        "room_id": 1,
                        "name": {
                            "it": "",
                            "en": "",
                            "es": "",
                            "fr": "",
                            "de": ""
                        },
                        "description": {
                            "it": "",
                            "en": "",
                            "es": "",
                            "fr": "",
                            "de": ""
                        },
                        "max_persons": 1,
                        "photos": [
                            {
                                "photo_id": input_data.get("main_photo_id", 1),
                                "url_original": input_data.get("main_photo_url", ""),
                                "url_max300": "",
                                "url_square85": ""
                            }
                        ],
                        "facilities": facilities_transformed,  # Facilities for rooms as well
                        "size_m2": 1
                    }
                ]
            }
        }
    }


async def transform_room_data(room_data: List[Union[RoomsData, Dict]],
                              disable_google_translations: bool = False) -> Dict:
    """
    Transforms room data by combining block information with room-specific details
    into a list of room objects instead of using room_id as keys.

    Args:
    room_data (List[Union[RoomsData, Dict]]): List of room data models or dictionaries.
    disable_google_translations (bool): If set to True, disables Google translations.

    Returns:
    Dict: Transformed room data combining block and room-specific details in a list of room objects.
    """
    rooms_transformed = []
    languages = ["it", "en", "es", "fr", "de"]  # Supported languages

    for room in room_data:
        # Handle both RoomsData (Pydantic) or raw dict
        blocks = room.block if isinstance(room, RoomsData) else room.get('block', [])
        rooms = room.rooms if isinstance(room, RoomsData) else room.get('rooms', {})  # noqa

        for block in blocks:
            # Handle both dict and Pydantic model
            room_id = block.room_id if isinstance(block, RoomsData) else block.get('room_id', "")  # noqa
            if not room_id:
                continue  # Skip if room_id is missing

            # Get room details from 'rooms' using room_id
            room_details = rooms.get(str(room_id), {})

            # Dynamic mapping of facilities from room details
            facilities = room_details.get("facilities", [])  # noqa

            # Combine photos from room details
            photos = room_details.get("photos", [])

            # Combine other room details such as private_bathroom_highlight, children_and_beds_text, etc.
            private_bathroom_highlight = room_details.get("private_bathroom_highlight", {})
            children_and_beds_text = room_details.get("children_and_beds_text", {})
            bed_configurations = room_details.get("bed_configurations", [])
            highlights = room_details.get("highlights", [])
            description = room_details.get("description", "")

            # Translate the name to multiple languages asynchronously if translation is not disabled
            room_name = block.name if isinstance(block, RoomsData) else block.get("name", "")  # noqa

            if room_name and not disable_google_translations:
                name_translations = await asyncio.gather(
                    *[async_translate(room_name, target_lang=lang) for lang in languages]
                )
                # Create a dictionary with translated names
                name_translated = {lang: translation for lang, translation in zip(languages, name_translations)}
            else:
                name_translated = {lang: room_name for lang in languages}  # Use original name if no translation

            # Translate the description to multiple languages asynchronously if translation is not disabled
            if description and not disable_google_translations:
                description_translations = await asyncio.gather(
                    *[async_translate(description, target_lang=lang) for lang in languages]
                )
                # Create a dictionary with translated descriptions
                description_translated = {lang: translation for lang, translation in
                                          zip(languages, description_translations)}
            else:
                description_translated = {lang: description for lang in
                                          languages}  # Use original description if no translation

            # Create the transformed room structure and append to list
            rooms_transformed.append({
                "hotel_id": room.hotel_id if isinstance(room, RoomsData) else room.get("hotel_id", ""),
                "room_id": room_id,
                "name": name_translated,  # Translated names or original name
                "description": description_translated,  # Translated descriptions or original description
                "max_persons": block.nr_adults if isinstance(block, RoomsData) else block.get("nr_adults", 1),  # noqa
                "photos": photos,
                "facilities": facilities,
                "size_m2": block.room_surface_in_m2 if isinstance(block, RoomsData) else block.get("room_surface_in_m2",
                                                                                                   1),  # noqa
                "private_bathroom_highlight": private_bathroom_highlight,
                "children_and_beds_text": children_and_beds_text,
                "bed_configurations": bed_configurations,
                "highlights": highlights
            })

    return {"rooms": rooms_transformed}


if __name__ == "__main__":
    # Define the path to your data.json file
    data_file = '../static/sample_rooms.json'

    # Open and load the JSON file
    with open(data_file, 'r', encoding='utf-8') as file:
        rooms = json.load(file)

    # Call the function and print the result
    transformed_rooms = transform_room_data(rooms)
    print(json.dumps(transformed_rooms, indent=2))
