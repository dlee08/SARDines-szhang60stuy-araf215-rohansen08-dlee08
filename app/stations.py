import csv
import os
from functools import lru_cache

STATIONS_CSV = os.path.join(os.path.dirname(__file__), "static", "MTA_Subway_Stations_20260515.csv")
STOP_DIRECTIONS = {
  "N": "northbound",
  "S": "southbound"
}

def parse_stop_id(stop_id):
  if not stop_id:
    return {
      "full_stop_id": None,
      "stop_id": None,
      "direction": None,
      "direction_name": None
    }

  direction = stop_id[-1] if stop_id[-1].isalpha() else None
  base_stop_id = stop_id[:-1] if direction else stop_id

  return {
    "full_stop_id": stop_id,
    "stop_id": base_stop_id,
    "direction": direction,
    "direction_name": STOP_DIRECTIONS.get(direction)
  }

@lru_cache(maxsize=1)
def get_station_lookup():
  stations = {}

  with open(STATIONS_CSV, newline="") as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
      stations[row["GTFS Stop ID"]] = {
        "stop_id": row["GTFS Stop ID"],
        "station_id": row["Station ID"],
        "complex_id": row["Complex ID"],
        "stop_name": row["Stop Name"],
        "borough": row["Borough"],
        "routes": row["Daytime Routes"],
        "lat": float(row["GTFS Latitude"]),
        "lng": float(row["GTFS Longitude"]),
        "north_label": row["North Direction Label"],
        "south_label": row["South Direction Label"]
      }

  return stations

def get_station_by_stop_id(stop_id):
  parsed_stop = parse_stop_id(stop_id)
  return get_station_lookup().get(parsed_stop["stop_id"])
