import json
from typing import List, Dict, Union

# Define the path to your data.json file
data_file = 'static/facilities.json'

# Open and load the JSON file
with open(data_file, 'r', encoding='utf-8') as file:
    facilities = json.load(file)


def map_facility_ids(facility_ids: List[int], facilities_list: List[Dict], lang: str, return_id: bool = False) -> List[Union[str, int]]:
    """
    Map facility IDs to their corresponding names in a specific language and exclude IDs that don't match any name.
    The function checks both 'hotel_facility_type_id' and 'facility_type_id'.
    If no matches are found, the facility will be excluded unless return_id is True, in which case the facility ID is returned.

    Args:
        facility_ids (List[int]): List of facility IDs to map.
        facilities_list (List[Dict]): List of facilities with 'name' field for different languages.
        lang (str): The language code for the name (e.g., 'en-gb', 'it', etc.)
        return_id (bool): If True, return the facility ID when no name is found, otherwise exclude the ID.

    Returns:
        List[Union[str, int]]: List of facility names in the specified language, or facility IDs if return_id is True.
    """
    facility_map = {}

    # Loop through facilities and map both 'hotel_facility_type_id' and 'facility_type_id' with names
    for facility in facilities_list:
        hotel_facility_type_id = facility.get('hotel_facility_type_id')
        facility_type_id = facility.get('facility_type_id')
        facility_name = facility.get('name', {})

        # Assign name based on the lang parameter or fallback to 'en-gb'
        if hotel_facility_type_id is not None:
            facility_map[hotel_facility_type_id] = facility_name.get(lang, facility_name.get('en-gb', None))

        if facility_type_id is not None:
            facility_map[facility_type_id] = facility_name.get(lang, facility_name.get('en-gb', None))

    # Return the facility names or facility IDs, and filter out entries with no match
    return [
        facility_map[facility_id] if facility_map.get(facility_id) is not None else facility_id
        for facility_id in facility_ids
        if facility_map.get(facility_id) is not None or return_id
    ]


# if __name__ == "__main__":
#     def main():
#         # Define the path to your data.json file
#         data_file = '../../static/facilities.json'
#
#         # Open and load the JSON file
#         with open(data_file, 'r', encoding='utf-8') as file:
#             facilities = json.load(file)
#
#         # Example usage of map_facility_ids function
#         facility_ids = [2, 3, 4, 5]
#         facilities_list = facilities  # Assuming facilities is a list of facility dictionaries
#         lang = 'en-gb'
#         mapped_facilities = map_facility_ids(facility_ids, facilities_list, lang)
#
#         print(mapped_facilities)
#
#     main()

