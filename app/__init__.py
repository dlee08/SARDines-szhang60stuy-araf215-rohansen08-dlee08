import csv

from flask import Flask, render_template, jsonify
from alerts import get_clean_alerts
from subway_api import parse_mta
import sqlalchemy as db
import pandas as pd
app = Flask(__name__)

env = open(".env")
key = env.readline().strip()
mkey = env.readline().strip()

engine = db.create_engine("sqlite:///NerdyMap.sqlite")
conn = engine.connect()
metadata = db.MetaData()

stops = db.Table('stops', metadata,
              db.Column('Id', db.Integer(),primary_key=True),
              db.Column('Name', db.String(255), nullable=False),
              db.Column('Major', db.String(255), default="Math"),
              db.Column('Pass', db.Boolean(), default=True)
              )

metadata.create_all(engine)

def parse_stations():
    with open("static/MTA_Subway_Stations_20260515.csv") as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        stops.insert()

stops = pd.read_csv("static/MTA_Subway_Stations_20260515.csv")
stops = pd.read_csv("static/MTA_Subway_Station_Complexes_20260518.csv")
stations_json = stops[['Stop Name', 'GTFS Latitude', 'GTFS Longitude', 'Daytime Routes']].to_json(orient='records')


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

if __name__ == "__main__":
    app.run(host='0.0.0.0')
