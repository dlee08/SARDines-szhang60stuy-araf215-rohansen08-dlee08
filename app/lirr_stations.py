import csv
import os
from functools import lru_cache

STATIONS_CSV = os.path.join(os.path.dirname(__file__), "static", "lirr.csv")

@lru_cache(maxsize=1)
def get_station_lookup():
  stations = {}
  with open(STATIONS_CSV, newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      stations[row["stop_id"]] = {
        "stop_id": row["stop_id"],
        "stop_name": row["stop_name"],
        "lat": float(row["stop_lat"]),
        "lng": float(row["stop_lon"]),
      }
  return stations

def get_station_by_stop_id_lirr(stop_id):
  if not stop_id:
    return None
  return get_station_lookup().get(stop_id)