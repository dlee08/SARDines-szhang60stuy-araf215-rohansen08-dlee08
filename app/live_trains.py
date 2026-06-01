from datetime import datetime, timezone
import json
from pprint import pprint

import requests
from google.transit import gtfs_realtime_pb2

from stations import get_station_by_stop_id, parse_stop_id


FEEDS = {
  "1234567": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
  "ace": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace",
  "bdfm": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm",
  "g": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g",
  "jz": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-jz",
  "l": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l",
  "nqrw": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw",
  "si": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-si",
}

MAX_VEHICLE_AGE_SECONDS = 900


def epoch_to_local(timestamp):
  if not timestamp:
    return None
  return datetime.fromtimestamp(int(timestamp), timezone.utc).astimezone().isoformat()


def fetch_feed(url):
  feed = gtfs_realtime_pb2.FeedMessage()
  response = requests.get(url, timeout=15)
  response.raise_for_status()
  feed.ParseFromString(response.content)
  return feed


def stop_details(stop_id):
  parsed = parse_stop_id(stop_id)
  station = get_station_by_stop_id(stop_id)

  return {
    "full_stop_id": parsed["full_stop_id"],
    "station_id": parsed["stop_id"],
    "direction": parsed["direction"],
    "direction_name": parsed["direction_name"],
    "station_name": station["stop_name"] if station else None,
    "lat": station["lat"] if station else None,
    "lng": station["lng"] if station else None,
  }


def first_future_stop(trip_update, now):
  for stop_time in trip_update.stop_time_update:
    arrival_time = stop_time.arrival.time if stop_time.HasField("arrival") else None
    departure_time = stop_time.departure.time if stop_time.HasField("departure") else None
    event_time = arrival_time or departure_time

    if event_time and event_time >= now:
      return {
        **stop_details(stop_time.stop_id),
        "arrival_time": epoch_to_local(arrival_time),
        "departure_time": epoch_to_local(departure_time),
        "epoch_arrival": arrival_time,
        "epoch_departure": departure_time,
      }

  return None

def all_future_stops(trip_update, now):
  stops = []
  for stop_time in trip_update.stop_time_update:
    arrival_time = stop_time.arrival.time if stop_time.HasField("arrival") else None
    departure_time = stop_time.departure.time if stop_time.HasField("departure") else None
    event_time = arrival_time or departure_time

    if event_time and event_time >= now:
      stops.append({
        **stop_details(stop_time.stop_id),
        "arrival_time": epoch_to_local(arrival_time),
        "departure_time": epoch_to_local(departure_time),
        "epoch_arrival": arrival_time,
        "epoch_departure": departure_time,
      })

  return stops


def collect_trip_updates(feed):
  updates = {}

  for entity in feed.entity:
    if entity.HasField("trip_update"):
      update = entity.trip_update
      updates[update.trip.trip_id] = update

  return updates


def vehicle_status_name(status):
  return gtfs_realtime_pb2.VehiclePosition.VehicleStopStatus.Name(status)


def is_live_vehicle(vehicle, now):
  if not vehicle.timestamp:
    return False

  age = now - vehicle.timestamp
  return 0 <= age <= MAX_VEHICLE_AGE_SECONDS


def is_self_targeting_report(current_stop, next_stop):
  if not next_stop:
    return True

  return current_stop["full_stop_id"] == next_stop["full_stop_id"]


def trip_stop_ids(trip_update):
  if not trip_update:
    return []

  return [stop_time.stop_id for stop_time in trip_update.stop_time_update]


def is_trip_endpoint_report(current_stop, trip_update):
  stop_ids = trip_stop_ids(trip_update)
  current_stop_id = current_stop["full_stop_id"]

  if not current_stop_id or not stop_ids:
    return False

  return current_stop_id == stop_ids[0] or current_stop_id == stop_ids[-1]


def updated_timestamp(train):
  if not train["last_updated"]:
    return 0

  return int(datetime.fromisoformat(train["last_updated"]).timestamp())


def remove_terminal_pileups(trains):
  terminal_trains = {}
  filtered_trains = []

  for train in trains:
    if not train["is_terminal_report"]:
      filtered_trains.append(train)
      continue

    key = (train["current_full_stop_id"], train["route_id"])
    existing_train = terminal_trains.get(key)

    if not existing_train or updated_timestamp(train) > updated_timestamp(existing_train):
      terminal_trains[key] = train

  return filtered_trains + list(terminal_trains.values())


def parse_live_trains():
  now = int(datetime.now(timezone.utc).timestamp())
  trains = []

  for feed_name, feed_url in FEEDS.items():
    feed = fetch_feed(feed_url)
    trip_updates = collect_trip_updates(feed)

    for entity in feed.entity:
      if not entity.HasField("vehicle"):
        continue

      vehicle = entity.vehicle
      if not is_live_vehicle(vehicle, now):
        continue

      trip_id = vehicle.trip.trip_id
      trip_update = trip_updates.get(trip_id)
      current_stop = stop_details(vehicle.stop_id) if vehicle.stop_id else stop_details(None)
      next_stop = first_future_stop(trip_update, now) if trip_update else None
      next_stops = all_future_stops(trip_update, now) if trip_update else None
      endpoint_report = is_trip_endpoint_report(current_stop, trip_update)
      if is_self_targeting_report(current_stop, next_stop) and not endpoint_report:
        continue

      trains.append({
        "feed": feed_name,
        "entity_id": entity.id,
        "trip_id": trip_id,
        "route_id": vehicle.trip.route_id,
        "current_status": vehicle_status_name(vehicle.current_status),
        "current_stop_sequence": vehicle.current_stop_sequence,
        "current_full_stop_id": current_stop["full_stop_id"],
        "current_station_id": current_stop["station_id"],
        "current_direction": current_stop["direction"],
        "current_direction_name": current_stop["direction_name"],
        "current_station_name": current_stop["station_name"],
        "lat": current_stop["lat"],
        "lng": current_stop["lng"],
        "next_stop": next_stop,
        "future_stops" : next_stops,
        "last_updated": epoch_to_local(vehicle.timestamp),
        "is_terminal_report": endpoint_report,
      })

  return remove_terminal_pileups(trains)

def get_times():
    now = int(datetime.now(timezone.utc).timestamp())
    trains = parse_live_trains()
    result = {}
    for train in trains:
        for stop in train.get("future_stops", []):
            if not stop.get("epoch_arrival"):
                continue
            next_time = int(stop["epoch_arrival"])
            data = {
                "route": train["route_id"],
                "direction": train["current_direction_name"],
                "current": train["current_station_name"],
                "next_stop": stop["station_name"],
                "local_time": stop["departure_time"],
                "time_to_arrive": str(round((next_time - now) / 60)) + " min",
            }
            station = stop["station_id"]
            result.setdefault(station, []).append(data)
    return result

if __name__ == "__main__":
  print(json.dumps(parse_live_trains(), indent=2))
  pprint(get_times())
