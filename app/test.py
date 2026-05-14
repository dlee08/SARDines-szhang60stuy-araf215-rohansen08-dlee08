import urllib.request
import json
from pprint import pprint

URL="https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/camsys%2Fsubway-alerts.json"

def call():
    global URL
    with urllib.request.urlopen(URL) as response:
        raw_data = response.read()
    data = json.loads(raw_data)
    meat = data['entity']
    cleaned_meat = []
    print(len(meat))
    for item in meat:
        alert = item["alert"]
        title =  alert["header_text"]["translation"][0]["text"]
        desc = alert.get("description_text", {
            "translation": [{"text": "There's no damn description"}]
        })["translation"][0]["text"]
        trains = []
        for i in alert["informed_entity"]:
            if "route_id" in i:
                trains.append(i["route_id"])
        cleaned_alert = {
            "id": item["id"],
            "trains": trains,
            "title":  title,
            "desc": desc
        }
        cleaned_meat.append(cleaned_alert)
    return  cleaned_meat
pprint(call())
