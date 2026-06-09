import json
import os
import numpy as np

from src.cycling_model import Cyclist

cyclist = Cyclist(150, 60, 12)


def create_time_matrix(wind_speed=0, wind_direction=0):
    # read locations
    with open("locations.json", "r") as f:
        locations = json.load(f)

    location_keys = list(locations.keys())

    files = os.listdir("routes")

    matrix = np.zeros((len(location_keys), len(location_keys)))

    for file in files:
        start_key, end_key = file[:-5].split("-")
        start_index = location_keys.index(start_key)
        end_index = location_keys.index(end_key)

        file_name = "routes/" + start_key + "-" + end_key + ".json"
        with open(file_name, "r") as f:
            route = json.load(f)

        points = np.array(route["paths"][0]["points"]["coordinates"])
        times = cyclist.time_to_travel(points[:-1], points[1:], wind_speed=wind_speed, wind_direction=wind_direction)
        matrix[start_index, end_index] = sum(times)

        times = cyclist.time_to_travel(points[::-1][:-1], points[::-1][1:], wind_speed=wind_speed, wind_direction=wind_direction)
        matrix[end_index, start_index] = sum(times)

    return location_keys, matrix

def create_distance_matrix():
    # read locations
    with open("locations.json", "r") as f:
        locations = json.load(f)

    location_keys = list(locations.keys())

    files = os.listdir("routes")

    matrix = np.zeros((len(location_keys), len(location_keys)))

    for file in files:
        start_key, end_key = file[:-5].split("-")
        start_index = location_keys.index(start_key)
        end_index = location_keys.index(end_key)

        file_name = "routes/" + start_key + "-" + end_key + ".json"
        with open(file_name, "r") as f:
            route = json.load(f)

        points = np.array(route["paths"][0]["points"]["coordinates"])
        times = cyclist.approximate_distance_from_latlon(points[:-1], points[1:])
        matrix[start_index, end_index] = sum(times)

        times = cyclist.approximate_distance_from_latlon(points[::-1][:-1], points[::-1][1:])
        matrix[end_index, start_index] = sum(times)

    return location_keys, matrix


def add_dummy_nodes(location_keys, matrix):
    # adds a single dummy node for start end location
    new_location_keys = ["DUMMY"] + location_keys
    new_matrix = np.zeros((len(new_location_keys), len(new_location_keys)))

    # copy old matrix into new matrix
    new_matrix[1:, 1:] = matrix

    return new_location_keys, new_matrix


# # print(create_time_matrix())

# file_name = "routes/" + "ADDINGTON" + "-" + "SUMNER" + ".json"
# with open(file_name, "r") as f:
#     route = json.load(f)

# points = np.array(route["paths"][0]["points"]["coordinates"])
# times = cyclist.approximate_distance_from_latlon(points[:-1], points[1:])

# print(sum(times))

# times = cyclist.time_to_travel(points[:-1], points[1:])

# print(sum(times))

