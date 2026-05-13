import urllib.request
import json
from pprint import pprint

URL="https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/camsys%2Fsubway-alerts.json"

def call(n):
    global URL
    with urllib.request.urlopen(URL) as response:
        raw_data = response.read()
    data = json.loads(raw_data)
    meat = data['entity']
    print(len(meat))
    return meat[n]

pprint(call(3))
