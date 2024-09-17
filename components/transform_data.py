import json
from typing import List, Dict
from dotenv import load_dotenv


def transform_data(input_data):
    # print(input_data)
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
                "facilities": {
                    "it": {
                        "typology": {
                            "it": "",
                            "en": "",
                            "es": "",
                            "fr": "",
                            "de": ""
                        },
                        "items": ["", "", ""]
                    },
                    "en": {},
                    "es": {},
                    "fr": {},
                    "de": {}
                },
                "number_of_rooms": 1,
                "description": {
                    "it": "",
                    "en": next((d["description"] for d in input_data.get("description_translations", []) if
                                d.get("languagecode") == "en-gb"), ""),
                    "es": "",
                    "fr": "",
                    "de": ""
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
                        "facilities": {
                            "it": ["", "", ""],
                            "en": ["", "", ""],
                            "es": ["", "", ""],
                            "fr": ["", "", ""],
                            "de": ["", "", ""]
                        },
                        "size_m2": 1
                    }
                ]
            }
        }
    }


def transform_room_data(room_data: List[Dict]) -> Dict:
    """
    Transforms room data by combining block information with room-specific details
    into a list of room objects instead of using room_id as keys.

    Args:
    room_data (List[Dict]): List of room data dictionaries containing both block and room-specific details.

    Returns:
    Dict: Transformed room data combining block and room-specific details in a list of room objects.
    """
    rooms_transformed = []

    languages = ["it", "en", "es", "fr", "de"]  # Supported languages

    for room in room_data:
        blocks = room.get('block', [])
        rooms = room.get('rooms', {})  # Get room-specific details from 'rooms' field

        for block in blocks:
            room_id = block.get("room_id", "")
            if not room_id:
                continue  # Skip if room_id is missing

            # Get room details from 'rooms' using room_id
            room_details = rooms.get(str(room_id), {})

            # Dynamic mapping of facilities from room details
            facilities = room_details.get("facilities", [])

            # Combine photos from room details
            photos = room_details.get("photos", [])

            # Combine other room details such as private_bathroom_highlight, children_and_beds_text, etc.
            private_bathroom_highlight = room_details.get("private_bathroom_highlight", {})
            children_and_beds_text = room_details.get("children_and_beds_text", {})
            bed_configurations = room_details.get("bed_configurations", [])
            highlights = room_details.get("highlights", [])
            description = room_details.get("description", "")

            # Create the transformed room structure and append to list
            rooms_transformed.append({
                "hotel_id": room.get("hotel_id", ""),
                "room_id": room_id,
                "name": {lang: block.get("name", "") for lang in languages},
                "description": description if description else {lang: block.get("room_name", "") for lang in languages},
                "max_persons": block.get("nr_adults", 1),
                "photos": photos,
                "facilities": facilities,
                "size_m2": block.get("room_surface_in_m2", 1) if block.get("room_surface_in_m2") else {},
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
