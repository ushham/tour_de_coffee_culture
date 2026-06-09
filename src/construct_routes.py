import json
import os
import requests
import yaml
import copy
import time

GRAPHHOPPER_URL = "https://graphhopper.com/api/1/route"

# read api key from yaml file
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

api_key = config["api"]

# read locations
with open("locations.json", "r") as f:
    locations = json.load(f)

location_keys = list(locations.keys())

def construct_api_call(start_key, end_key):
    start_coords = locations[start_key]
    end_coords = locations[end_key]

    # Construct the API call URL
    payload = {
        "points": [
            [
                start_coords["lon"],
                start_coords["lat"]
            ],
            [
                end_coords["lon"],
                end_coords["lat"]
            ]
        ],
        "profile": "bike",
        "locale": "en",
        "instructions": False,
        "calc_points": True,
        "points_encoded": False,
        "elevation": True
        }

    response = requests.post(GRAPHHOPPER_URL, params={"key": api_key}, json=payload)
    response.raise_for_status()
    
    # Returns a 2D array of travel times in seconds
    return response.json()


def reverse_route(d):
    new_dic = copy.deepcopy(d)
    new_dic["paths"][0]["points"]["coordinates"] = d["paths"][0]["points"]["coordinates"][::-1]


def save_route(start, end, route):
    file_name = "routes/" + start + "-" + end + ".json"
    with open(file_name, "w") as f:
        json.dump(route, f)


def route_exists(start, end):
    file_name = "routes/" + start + "-" + end + ".json"
    return os.path.exists(file_name)


location_keys = ["KAIAPOI", "REDWOOD"]

for i, start_key in enumerate(location_keys):
    for end_key in location_keys[i + 1 :]:
        print(start_key + " " + end_key)
        if not(route_exists(start_key, end_key)):
            time.sleep(10)
            rt = construct_api_call(start_key, end_key)
            save_route(start_key, end_key, rt)   

