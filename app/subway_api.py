from google.transit import gtfs_realtime_pb2
import requests

train_path = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs"

feed = gtfs_realtime_pb2.FeedMessage()
response = requests.get(train_path)
feed.ParseFromString(response.content)
for entity in feed.entity:
  if entity.HasField('trip_update'):
    print(entity.trip_update)
