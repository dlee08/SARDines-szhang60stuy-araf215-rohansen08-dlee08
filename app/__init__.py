import csv

from flask import Flask, render_template, jsonify
from alerts import get_clean_alerts
from subway_api import parse_mta
from live_trains import parse_live_trains, get_times, parse_live_lirr
from elev_esca import parse_elev_esca
import sqlalchemy as db
import pandas as pd
from datetime import time, datetime
app = Flask(__name__)

env = open(".env")
key = env.readline().strip()
mkey = env.readline().strip()

stops = pd.read_csv("static/MTA_Subway_Stations_20260515.csv")
railroads = pd.read_csv("static/MTA_Rail_Stations_20260604.csv")

def merge_routes(series):
    routes = []
    for val in series:
        routes.extend(val.split())
    return " ".join(sorted(set(routes)))

complex_stops = (
    stops.groupby("Complex ID", as_index=False)
    .agg({
        "Stop Name": "first",
        "Station ID": "first",
        "GTFS Latitude": "first",
        "GTFS Longitude": "first",
        "Daytime Routes": merge_routes
    })
)

stations_json = complex_stops[
    ["Stop Name", "GTFS Latitude", "GTFS Longitude", "Daytime Routes", "Complex ID"]
].to_json(orient="records")

railroad_stations_json = railroads[
    [
        "Railroad",
        "Code",
        "Station Name",
        "Branch",
        "Latitude",
        "Longitude",
        "Outbound Title",
        "Inbound Title",
        "Zone",
        "Accessibility",
        "Station URL"
    ]
].to_json(orient="records")

@app.route("/")
def hello():
    now = datetime.now().time()
    is_late_night = now >= time(23, 0) or now < time(5, 0)
    return render_template("map_temp.html", api_key=key, map_key=mkey, data=stops, stations=stations_json, railroad_stations=railroad_stations_json, night=is_late_night)

@app.route("/api/alerts")
def api_alerts():
    alerts = get_clean_alerts()
    return jsonify(alerts)

@app.route("/api/trains")
def api_trains():
    trains = parse_mta()
    return jsonify(trains)

@app.route("/api/live_lirr")
def api_lirr():
    trains = parse_live_lirr()
    return jsonify(trains)

@app.route("/api/live_trains")
def api_livetrains():
    return jsonify(parse_live_trains())

@app.route("/api/elevator")
def api_elevator():
    return jsonify(parse_elev_esca())

@app.route("/api/stop_times")
def api_stop_times():
    return jsonify(get_times())

if __name__ == "__main__":
    app.run(host='0.0.0.0')
