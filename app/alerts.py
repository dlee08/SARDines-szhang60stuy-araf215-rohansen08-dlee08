import urllib.request
import json
import time
from pprint import pprint
from stations import get_station_by_stop_id, parse_stop_id

URL="https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/camsys%2Fsubway-alerts.json"

alert_types_filter =  {
    "No Scheduled Service",
    "Reduced Service",
    "Delays",
    "Express to Local"
}

route_names = {
 "GS": "42nd Street Shuttle",      # 42nd st shuttle
 "FS": "Franklin Avenue Shuttle",      # Franklin ave shuttle
 "H": "Rockaway Park Shuttle",       # Rockaway park shuttle
 "SI": "Staten Island Railway"     # Staten island railway
}

alert_severity =  {
    "Delays": "high",
    "No Scheduled Service": "high",
    "Reduced Service": "medium",
    "Express to Local": "low"
}

def get_translation_text(field, fallback="No information available"):
    """
     Grabs text from the MTA translation fields in the json endpoint.
    """
    if not field:
        return fallback

    translations = field.get("translation", [])
    if not translations:
        return fallback

    return translations[0].get("text", fallback)

def fetch_alert_feed():
    """
    Gets raw subway alert data from the endpoint.
    """
    global URL

    with urllib.request.urlopen(URL) as response:
        raw_data = response.read()

    return json.loads(raw_data)

def clean_route(route_id):
    """
    Returns the route name, which is the route id.
    The name field is mainly to convert ids like "GS" to "42nd St Shuttle" via our route_names array.
    """
    return {
        "route id": route_id,
        "name": route_names.get(route_id, route_id),
        "icon": f"/static/svg/{route_id.lower()}.svg" # Added in icon support for when we code our front end
    }

def clean_alert(item):
    """
    Turns one raw MTA alert into frontend friendly data.
    """
    alert = item.get("alert", {})

    alert_type = alert.get("transit_realtime.mercury_alert", {}).get("alert_type")

    #if alert_type not in alert_types_filter:
    #    return None

    title = get_translation_text(alert.get("header_text"), "Untitled alert")
    description = get_translation_text(alert.get("description_text"))

    routes = []
    stops = []
    seen_routes = set()
    seen_stops = set()

    for entity in alert.get("informed_entity", []):
        route_id = entity.get("route_id")
        stop_id = entity.get("stop_id")

        if route_id and route_id not in seen_routes:
            routes.append(clean_route(route_id))
            seen_routes.add(route_id)

        if stop_id and stop_id not in seen_stops:
            parsed_stop = parse_stop_id(stop_id)
            stops.append({
                "full_stop_id": parsed_stop["full_stop_id"],
                "stop_id": parsed_stop["stop_id"],
                "direction": parsed_stop["direction"],
                "direction_name": parsed_stop["direction_name"],
                "station": get_station_by_stop_id(stop_id)
            })
            seen_stops.add(stop_id)

    return {
        "id": item.get("id"),
        "type": alert_type,
        "severity": alert_severity.get(alert_type, "low"),
        "title": title,
        "description": description,
        "routes": routes,
        "route_count": len(routes),
        "stops": stops,
        "stop_count": len(stops)
    }

def is_current(alert):
    full_times = alert.get('alert').get('active_period')
    #pprint(full_times)
    current_time = int(time.time())
    for active_time in full_times:
        start = active_time['start']
        #print(f"current: {current_time}, start: {start}")
        if current_time > start:
            #print("passed stage 1")
            if len(active_time) > 1 and active_time['end'] > current_time:
                #print("end included")
                return True
            else:
                #print("end not included")
                return True
    return False

def get_clean_alerts():
    """
    Gets all alerts and returns only the cleaned wanted ones.
    If the MTA API fails, return an empty list instead of crashing the app.
    """
    try:
        data = fetch_alert_feed()
        entities = data.get("entity", [])

        cleaned_alerts = []

        for item in entities:
            if is_current(item):
                cleaned = clean_alert(item)
                cleaned_alerts.append(cleaned)
        print(len(cleaned_alerts))
        return cleaned_alerts

    except Exception as e:
        print("Alert API error:", e)
        return []

if __name__ == "__main__":
    get_clean_alerts()
