import urllib.request
import json
from pprint import pprint
from stations import get_station_by_stop_id, parse_stop_id

URL="https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fnyct_ene.json"

def fetch_feed():
    """
    Gets raw elevator and escalator status data from the endpoint.
    """
    global URL

    with urllib.request.urlopen(URL) as response:
        raw_data = response.read()

    return json.loads(raw_data)

def parse_elev_esca():
	try:
		feed = fetch_feed()
		results = []
		for status in feed:
			#pprint(status)
			if status['isupcomingoutage'] == 'N':
				details = {
					"type" : status['equipmenttype'],
					"est_return" : status['estimatedreturntoservice'],
					"outage_date" : status['outagedate'],
					"reason" : status['reason'],
					"serving_info" : status['serving'], 
					"station" : status['station'], 
					"trainno" : status['trainno'].split('/')
				}
				results.append(details)
		return results
	except Exception as e:
		print("Elevator/Escalator API error:", e)
		return  []

#pprint(parse_elev_esca())