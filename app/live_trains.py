from datetime import datetime, timezone
import json

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
      }

  return None


def collect_trip_updates(feed):
  updates = {}

  for entity in feed.entity:
    if entity.HasField("trip_update"):
      update = entity.trip_update
      updates[update.trip.trip_id] = update

  return updates


def vehicle_status_name(status):
  return gtfs_realtime_pb2.VehiclePosition.VehicleStopStatus.Name(status)


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
      trip_id = vehicle.trip.trip_id
      trip_update = trip_updates.get(trip_id)
      current_stop = stop_details(vehicle.stop_id) if vehicle.stop_id else stop_details(None)
      next_stop = first_future_stop(trip_update, now) if trip_update else None

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
        "next_stop": next_stop,
        "last_updated": epoch_to_local(vehicle.timestamp),
      })

  return trains


if __name__ == "__main__":
  print(json.dumps(parse_live_trains(), indent=2))
