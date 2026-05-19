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
# complexes = pd.read_csv("static/MTA_Subway_Station_Complexes_20260518.csv")
# concat = ""
# for cmp in complexes:
#     df = stops.loc[stops['Complex ID'] == complexes['Complex ID'][0]]
#     for stop in df:
#         concat+=" "+df['Daytime Routes'][0]
#     df[0]['Daytime Routes'] = concat
#     concat = ''
stations_json = stops[['Stop Name', 'GTFS Latitude', 'GTFS Longitude', 'Daytime Routes', 'Complex ID']].to_json(orient='records')

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
