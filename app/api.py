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
    #pprint(meat[2])
    cleaned_meat = []
    alert_types_filter =  {
        "No Scheduled Service",
        "Reduced Service",
        "Delays",
        "Express to Local"
    }
    route_names = {
    "GS": "42nd Street Shuttle",      # 42nd st shuttle
    "FS": "Franklin ave Shuttle",      # Franklin ave shuttle
    "H": "Rockaway Park Shuttle",       # Rockaway park shuttle
    "SI": "SIR"     # Staten island railway
    }
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
                route = i["route_id"]
                if route in route_names:
                    route =  route_names[route]
                if route not in trains:
                    trains.append(route)
        type = alert['transit_realtime.mercury_alert']['alert_type']
        if type not in alert_types_filter:
            continue
        cleaned_alert = {
            "id": item["id"],
            "trains": trains,
            "title":  title,
            "desc": desc,
            "type": type # 'No Scheduled Service', 'Reduced Service', 'Delays', 'Express to Local'
        }
        cleaned_meat.append(cleaned_alert)
    return  cleaned_meat
pprint(call())
#call()
