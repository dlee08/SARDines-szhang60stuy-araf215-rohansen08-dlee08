from google.transit import gtfs_realtime_pb2
import requests
from datetime import datetime, timezone
from pprint import pprint

TRAIN_PATH = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs"

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
        "depart_time" : None,
        "arrive_time" : None,
        "route_id" : update.trip.route_id
      }
      #print(update)
      for stu in update.stop_time_update:
        if stu.HasField('arrival'):
          trip["arrive"] = stu.stop_id
          trip["arrive_time"] = epoch_to_local(stu.arrival.time)
        if stu.HasField('departure'):
          trip["depart"] = stu.stop_id
          trip["depart_time"] = epoch_to_local(stu.departure.time)
      #for stop_update in entity:
      #  print(stop_update)

    results.append(trip)
  return results

#parse_mta()
pprint(parse_mta())