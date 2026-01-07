# Link arrivals board OneBusAway API proxy server
# Responses from the OBA API are cached for 30 seconds

import numpy as np
import secret
import requests
import time
from datetime import datetime

# yes i know this should probably be in a class

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
                if services["departureEnabled"]: # services["predicted"] is false right now?
                    time_to_go = (int(services["predictedArrivalTime"]) - current_time) / 1000 / 60
                    stops_away = int(services["numberOfStopsAway"])
                    if stops_away > 0:
                        print("")
                        print("predicted: " + str(services["predicted"]))
                        print("time to go (min): " + str(int(time_to_go)))
                        print("closest stop: " + str(get_stop_name(services["tripStatus"]["closestStop"])))
                        print("stops away: " + str(services["numberOfStopsAway"]))
                        
                        # get train direction
                        # TRUE = going north
                        # FALSE = going south
                        direction = get_stop_direction(stop_id=services["tripStatus"]["closestStop"])
                        print("direction: " + str(direction))

def get_stop_direction(stop_id):
    # get stop value
    polarizing_stop = 'Beacon Hill'
    stop_ids_map = np.loadtxt("stops.txt", delimiter=",", dtype=str)

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
        
def get_stop_name(stop_id):
    stop_ids_numbered = np.loadtxt("stops.txt", delimiter=",", dtype=str)

    for stop in stop_ids_numbered:
        if stop_id == stop[0]:
            return stop[1]
        
# load_stop_names()
get_beacon_hill_stop()