# Link arrivals board OneBusAway API proxy server
# Responses from the OBA API are cached for 30 seconds

import os
import numpy as np
import secret
import requests
import time
from datetime import datetime
from io import BytesIO
from zipfile import ZipFile
from flask import Flask, Response, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from apscheduler.schedulers.background import BackgroundScheduler
from waitress import serve

server = Flask(__name__)
CORS(server)
limiter = Limiter(
    key_func=get_remote_address,
    app=server,
    default_limits=['600 per hour', '1 per second'],
)

scheduler = BackgroundScheduler()

gtfs_url = 'https://www.soundtransit.org/GTFS-rail/40_gtfs.zip'
routes = {
    '1_100224': {}, # 1 line
    # '40_2LINE': {},
    # '40_TLINE': {},
    # '40_SNDR_TL': {}, # Sounder S line (seattle - tacoma dome/lakewood)
    # '40_SNDR_EV': {} # Sounder N line (seattle - everett)
}
route_metadata = {}
cache = {}

def make_request(url):
    cached_request = cache.get(url, [None, 0])
    current_time = int(time.time())
    if (current_time - cached_request[1] < 30):
        return cached_request[0]

    new_request = requests.get(url)
    cached_request[0] = new_request.json()
    cached_request[1] = current_time
    cache[url] = cached_request

    return cached_request[0]

def load_stop_names():
    route_id = "40_100479" # 1 line
    url = "https://api.pugetsound.onebusaway.org/api/where/stops-for-route/" + route_id + ".json?key=" + secret.api_key
    print(url)
    data = requests.get(f'{url}').json()

    # get direction of stops
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
                        # print(stop["name"])
                        stop_id_to_name[i, 0] = stop["id"]
                        stop_id_to_name[i, 1] = stop["name"]
                        stop_id_to_name[i, 2] = i
                        # print(stop["id"])
                        # print(" ")
                        i += 1
                        # this will overflow because the sorted list's has 2 extra elements
                        # blame SoundTransit
        # print(stop_id_to_name)    

def get_beacon_hill_stop():
    # agency ID for one line: 40
    # 1 line ID: 40_100479
    stop_id = "40_99240"
    url = "https://api.pugetsound.onebusaway.org/api/where/arrivals-and-departures-for-stop/" + stop_id + ".json?key=" + secret.api_key
    print(url)
    data = requests.get(f'{url}').json()
    current_time = int(data["currentTime"])
    incoming = data["data"]["entry"]["arrivalsAndDepartures"]
    for services in incoming:
        print(services["routeShortName"])
        if services["routeShortName"] == "1 Line":
            print(services["numberOfStopsAway"])
            if services["predicted"] and services["departureEnabled"]:
                print("")
                time_to_go = (int(services["predictedArrivalTime"]) - current_time) / 1000 / 60
                print(int(time_to_go))
                print(services["tripStatus"]["closestStop"])
                print(services["numberOfStopsAway"])
                # TODO: figure out north and south

def get_stop_direction(stop_id):
    polarizing_stop = "Beacon Hill" # TODO: get Beacon Hill stop value
    stop_ids_numbered = np.loadtxt("ordered_stops.txt")

    for stop in stop_ids_numbered:
        if stop_id == stop[0]:
            return stop[2] > polarizing_stop # TODO: figure out logic

# load_stop_names()
get_beacon_hill_stop()

# scheduler.add_job(update_gtfs, trigger='interval', days=1, id='update_gtfs', next_run_time=datetime.now())
# scheduler.start()
#serve(server, host='0.0.0.0', port=2053) ONLY UNCOMMENT if you're not using another WSGI server; only http will work