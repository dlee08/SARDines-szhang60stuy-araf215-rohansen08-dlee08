from google.transit import gtfs_realtime_pb2
import requests
from datetime import datetime, timezone
from pprint import pprint
from stations import get_station_by_stop_id

TRAIN_PATH = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs"
STOP_DIRECTIONS = {
  "N": "northbound",
  "S": "southbound"
}

# translates epoch time to local time 1779073290 -> ('2026-05-17', ['23', '01', '30'])
def epoch_to_local(time): 
  if time is None:
    return None
  else:
    time = datetime.fromtimestamp(int(time), timezone.utc).astimezone()
    time = time.isoformat()
    time = time.split("T")
    day = time[0]
    time = time[1].split("-")[0].split(":")
    return day, time

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

def parse_mta():
  feed = gtfs_realtime_pb2.FeedMessage()
  response = requests.get(TRAIN_PATH)
  feed.ParseFromString(response.content)
  results = []
  for entity in feed.entity:
    if entity.HasField('trip_update'):
      update = entity.trip_update
      trip = {
        "depart" : None,
        "arrive" : None,
        "depart_full_stop_id" : None,
        "depart_stop_id" : None,
        "depart_direction" : None,
        "depart_direction_name" : None,
        "depart_station" : None,
        "arrive_full_stop_id" : None,
        "arrive_stop_id" : None,
        "arrive_direction" : None,
        "arrive_direction_name" : None,
        "arrive_station" : None,
        "depart_time" : None,
        "arrive_time" : None,
        "route_id" : update.trip.route_id
      }
      #print(update)
      for stu in update.stop_time_update:
        if stu.HasField('arrival'):
          arrive_stop = parse_stop_id(stu.stop_id)
          trip["arrive"] = stu.stop_id
          trip["arrive_full_stop_id"] = arrive_stop["full_stop_id"]
          trip["arrive_stop_id"] = arrive_stop["stop_id"]
          trip["arrive_direction"] = arrive_stop["direction"]
          trip["arrive_direction_name"] = arrive_stop["direction_name"]
          trip["arrive_station"] = get_station_by_stop_id(stu.stop_id)
          trip["arrive_time"] = epoch_to_local(stu.arrival.time)
        if stu.HasField('departure'):
          depart_stop = parse_stop_id(stu.stop_id)
          trip["depart"] = stu.stop_id
          trip["depart_full_stop_id"] = depart_stop["full_stop_id"]
          trip["depart_stop_id"] = depart_stop["stop_id"]
          trip["depart_direction"] = depart_stop["direction"]
          trip["depart_direction_name"] = depart_stop["direction_name"]
          trip["depart_station"] = get_station_by_stop_id(stu.stop_id)
          trip["depart_time"] = epoch_to_local(stu.departure.time)
      #for stop_update in entity:
      #  print(stop_update)

      results.append(trip)
  return results

if __name__ == "__main__":
  pprint(parse_mta())
