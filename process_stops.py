import numpy as np
import requests
import secret

def load_stop_names():
    route_id = "40_100479" # 1 line
    url = "https://api.pugetsound.onebusaway.org/api/where/stops-for-route/" + route_id + ".json?key=" + secret.api_key
    print(url)
    data = requests.get(f'{url}').json()

    # get stops sorted by direction (North to South)
    stop_direction = data["data"]["entry"]["stopGroupings"][0]["stopGroups"][0]["stopIds"]
    # print(stop_direction)

    # get mapping of stops to IDs
    # fuck it we brute force
    stops = data["data"]["references"]["stops"]
    stop_id_to_name = np.empty((78, 4), dtype=object)
    i = 0
    already_in_list = False
    starting_stop = "Lynnwood City Center"
    stop_index = 0
    for north_to_south in stop_direction:
        # print(north_to_south)
        for stop in stops:
            if stop["id"] == north_to_south:
                stop_name = stop["name"]
                for stop in stops:
                    if stop["name"] == stop_name:
                        for prev_stop in stop_id_to_name:
                            if prev_stop[0] == stop["id"]:
                                already_in_list = True
                        if not already_in_list:
                            stop_id_to_name[i, 0] = stop["id"]
                            stop_id_to_name[i, 1] = stop["name"]
                            stop_id_to_name[i, 2] = i
                            if stop_id_to_name[i, 1] != starting_stop:
                                stop_index += 1
                                starting_stop = stop_id_to_name[i, 1]
                            stop_id_to_name[i, 3] = str(stop_index)
                            i += 1
                    already_in_list = False
    np.savetxt("ordered_stops.txt", stop_id_to_name, delimiter=",", fmt='%s')
    # print(stop_id_to_name)  

def stop_name_to_value():
    # process stops, check if it's a new stop, and if so give it a new number
    # probably would've been faster to just do this by hand

    stop_ids_numbered = np.loadtxt("ordered_stops.txt", delimiter=",", dtype=str)
    stop_ids_map = np.empty((104, 4), dtype=object)
    starting_stop = "Lynnwood City Center"
    stop_index = 0
    for i in range(len(stop_ids_numbered)):
        stop_ids_map[i, 0] = stop_ids_numbered[i, 0].strip("' ")
        stop_ids_map[i, 1] = stop_ids_numbered[i, 1].strip("' ")
        stop_ids_map[i, 2] = stop_ids_numbered[i, 2].strip("' ")

        if stop_ids_map[i, 1] != starting_stop:
            stop_index += 1
            starting_stop = stop_ids_map[i, 1]

        stop_ids_map[i, 3] = str(stop_index)
    np.savetxt("stops.txt", stop_ids_map, delimiter=",", fmt='%s')

load_stop_names()
