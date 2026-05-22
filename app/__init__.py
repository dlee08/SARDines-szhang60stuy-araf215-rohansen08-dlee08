import csv

from flask import Flask, render_template, jsonify
from alerts import get_clean_alerts
from subway_api import parse_mta
from live_trains import parse_live_trains
from elev_esca import parse_elev_esca
import sqlalchemy as db
import pandas as pd
app = Flask(__name__)

env = open(".env")
key = env.readline().strip()
mkey = env.readline().strip()

stops = pd.read_csv("static/MTA_Subway_Stations_20260515.csv")

def merge_routes(series):
    routes = []
    for val in series:
        routes.extend(val.split())
    return " ".join(sorted(set(routes)))

complex_stops = (
    stops.groupby("Complex ID", as_index=False)
    .agg({
        "Stop Name": "first",
        "GTFS Latitude": "first",
        "GTFS Longitude": "first",
        "Daytime Routes": merge_routes
    })
)

stations_json = complex_stops[
    ["Stop Name", "GTFS Latitude", "GTFS Longitude", "Daytime Routes", "Complex ID"]
].to_json(orient="records")
@app.route("/")
def hello():
    return render_template("map_temp.html", api_key=key, map_key=mkey, data=stops, stations=stations_json)

@app.route("/api/alerts")
def api_alerts():
    alerts = get_clean_alerts()
    return jsonify(alerts)

@app.route("/api/trains")
def api_trains():
    trains = parse_mta()
    return jsonify(trains)

@app.route("/api/live_trains")
def api_livetrains():
    return jsonify(parse_live_trains())

@app.route("/api/elevator")
def api_elevator():
    return jsonify(parse_elev_esca())

if __name__ == "__main__":
    app.run(host='0.0.0.0')
