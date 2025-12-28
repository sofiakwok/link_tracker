# Link arrivals board OneBusAway API proxy server
# Responses from the OBA API are cached for 30 seconds

import numpy as np
import secret
import requests
import time
from datetime import datetime

def load_stop_names():
    route_id = "40_100479" # 1 line
    url = "https://api.pugetsound.onebusaway.org/api/where/stops-for-route/" + route_id + ".json?key=" + secret.api_key
    print(url)
    data = requests.get(f'{url}').json()

    # get stops sorted by direction (North to South)
    stop_direction = data["data"]["entry"]["stopGroupings"][0]["stopGroups"][0]["stopIds"]
    print(stop_direction)

    # get mapping of stops to IDs
    # fuck it we brute force
    stops = data["data"]["references"]["stops"]
    stop_id_to_name = np.empty((len(stops), 3), dtype=object)
    i = 0
    for north_to_south in stop_direction:
        print(north_to_south)
        for stop in stops:
            if stop["id"] == north_to_south:
                stop_name = stop["name"]
                for stop in stops:
                    if stop["name"] == stop_name:
                        stop_id_to_name[i, 0] = stop["id"]
                        stop_id_to_name[i, 1] = stop["name"]
                        stop_id_to_name[i, 2] = i
                        i += 1
                        # this will overflow because the sorted list has 2 extra elements
                        # blame SoundTransit
        # print(stop_id_to_name)    

def get_beacon_hill_stop():
    # agency ID for one line: 40
    # 1 line ID: 40_100479
    # incredibly goofy setup in the API where the north and south trains have diff stop names
    stop_ids = ["40_99240", '40_C19', '40_99121']
    for stop_id in stop_ids:
        # print(stop_id)
        url = "https://api.pugetsound.onebusaway.org/api/where/arrivals-and-departures-for-stop/" + stop_id + ".json?key=" + secret.api_key
        # print(url)
        data = requests.get(f'{url}').json()
        current_time = int(data["currentTime"])
        incoming = data["data"]["entry"]["arrivalsAndDepartures"]
        for services in incoming:
            if services["routeShortName"] == "1 Line":
                if services["predicted"] and services["departureEnabled"]:
                    time_to_go = (int(services["predictedArrivalTime"]) - current_time) / 1000 / 60
                    if time_to_go > 0:
                        print("")
                        print("predicted: " + str(services["predicted"]))
                        print("time to go (min): " + str(int(time_to_go)))
                        print("closest stop: " + str(services["tripStatus"]["closestStop"]))
                        print("stops away: " + str(services["numberOfStopsAway"]))
                        
                        # get train direction
                        # TRUE = going north
                        # FALSE = going south
                        direction = get_stop_direction(stop_id=services["tripStatus"]["closestStop"])
                        print("direction: " + str(direction))

def get_stop_direction(stop_id):
    # get stop value
    polarizing_stop = 'Beacon Hill'
    stop_ids_numbered = np.loadtxt("ordered_stops.txt", delimiter=",", dtype=str)

    # strip leading and trailing characters for each value
    # stupid bug
    stop_ids_map = np.empty(np.shape(stop_ids_numbered), dtype=object)
    for i in range(len(stop_ids_numbered)):
        stop_ids_map[i, 0] = stop_ids_numbered[i, 0].strip("' ")
        stop_ids_map[i, 1] = stop_ids_numbered[i, 1].strip("' ")
        stop_ids_map[i, 2] = stop_ids_numbered[i, 2].strip("' ")

    # finding stop val range for polarizing stop
    start_val = 0
    for stop in stop_ids_map:
        if stop[1] == polarizing_stop:
            start_val = int(stop[2])
            break

    # get whether train is coming from north or south
    for stop in stop_ids_map:
        if stop_id == stop[0]:
            # if this is TRUE then the train is going north
            return int(stop[2]) > start_val

# load_stop_names()
while True:
    get_beacon_hill_stop()
    time.sleep(30)