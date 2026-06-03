import urllib.request
import json
import time
import re
import html
from pprint import pprint
from stations import get_station_by_stop_id, parse_stop_id

URL="https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/camsys%2Fsubway-alerts.json"



route_names = {
 "GS": "S",      # 42nd st shuttle
 "FS": "SF",      # Franklin ave shuttle
 "H": "SR",       # Rockaway park shuttle
 "SI": "SIR"     # Staten island railway
}

def format_route_list(routes):
    if not routes:
        return ""

    if len(routes) == 1:
        return routes[0]
    if len(routes) == 2:
        return f"{routes[0]} and {routes[1]}"

    return ", ".join(routes[:-1]) + f", and {routes[-1]}"

def clean_text(text):
    if not text:
        return "No information available"

    text = html.unescape(text)
    text = re.sub(r"<br\s*/?>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)

    def replace_bracket_group(match):
        group = match.group(0)
        routes = re.findall(r"\[([A-Z0-9]+)\]", group)
        return format_route_list(routes)

    text = re.sub(r"(?:\[[A-Z0-9]+\])+", replace_bracket_group, text)
    text = re.sub(r"\s+", " ", text).strip()

    return text

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
    if route_id.lower()=="gs":
        route_id="s"
    if route_id.lower()=="si":
        route_id="sir"
    if route_id.lower()=="fs":
        route_id="sf"
    if route_id.lower()=="rs":
        route_id="sr"
    if route_id.lower()=="h":
        route_id="sr"
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


    title = clean_text(get_translation_text(alert.get("header_text"), "Untitled alert"))
    description = clean_text(get_translation_text(alert.get("description_text")))

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
        "title": title,
        "description": description,
        "routes": routes,
        "route_count": len(routes),
        "stops": stops,
        "stop_count": len(stops)
    }

def is_current(alert):
    full_times = alert.get('alert', {}).get('active_period', [])
    #pprint(full_times)
    current_time = int(time.time())
    for active_time in full_times:
        start = active_time.get('start')
        end = active_time.get('end')
        #print(f"current: {current_time}, start: {start}")
        if start is None:
            continue
        if current_time >= start:
            if end is None or end > current_time:
                #print("end included")
                #print(f"current: {current_time}, start: {start}, end: {end}")
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
                #pprint(cleaned)

        return sort_alerts(cleaned_alerts)

    except Exception as e:
        print("Alert API error:", e)
        return []

def find_best_route(targ_alert):
    targ_routes =[]
    for targ_route in targ_alert['routes']:
        targ_routes.append(targ_route['route id'])
    #print(targ_routes)
    best_targ_route = targ_routes[0]
    if len(targ_routes) > 1:
        for targ_route in targ_routes:
            if targ_route < best_targ_route:
                best_targ_route = targ_route
    #print(best_targ_route)
    return best_targ_route

def sort_alerts(alerts):
    sorted = []
    for targ_alert in alerts:
        targ_route = find_best_route(targ_alert)
        sorted.append(targ_alert)
        for i in range(len(sorted)):
            curr_route = find_best_route(sorted[i])
            if targ_route < curr_route:
                swap = sorted[i]
                sorted[i] = sorted[len(sorted) - 1]
                sorted[len(sorted) - 1] = swap
    return sorted

if __name__ == "__main__":
    pprint(get_clean_alerts())
    #get_clean_alerts()
