from flask import Flask, render_template
from google.transit import gtfs_realtime_pb2
import requests
app = Flask(__name__)

feed = gtfs_realtime_pb2.FeedMessage()
response = requests.get('https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace')
feed.ParseFromString(response.content)
for entity in feed.entity:
  if entity.HasField('trip_update'):
    print(entity.trip_update)

key = open(".env").read().strip()

@app.route("/")
def hello():
    return render_template("map_temp.html", api_key=key)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
