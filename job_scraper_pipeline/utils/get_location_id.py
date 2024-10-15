from ..scraper.db_requests.get_db_locations import location_find_first


def get_location_id(location_plan_text):
    if ',' in location_plan_text:
        city, state = location_plan_text.split(', ', 1)

        # filter for state can be either abbreviation or full name
        db_location = location_find_first(city, state)

    if db_location is None:
        print('location not found >', city, state)
    else:
        # print(f"{locations_response['id']} > {city}, {state}")
        return db_location['id']