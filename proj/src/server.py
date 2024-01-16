from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import requests
from urllib.parse import urlparse
import threading
import time
from orion_helper import fetch_data_from_orion


# NASA to Orion integration
NASA_API_URL = "https://data.nasa.gov/resource/gh4g-9sfh.json"
ORION_URL = "http://localhost:1026/ngsi-ld/v1/entities"
NGSI_LD_CONTEXT = "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"

def fetch_nasa_data():
    response = requests.get(NASA_API_URL)
    return response.json()

def transform_to_ngsi(nasa_data):
    ngsi_entities = []
    for item in nasa_data:
        
        if 'geolocation' in item and 'latitude' in item['geolocation'] and 'longitude' in item['geolocation']:
            ngsi_entity = {
                "id": f"urn:ngsi-ld:Asteroid:{item['id']}",
                "type": "Asteroid",
                "@context": NGSI_LD_CONTEXT,
                "name": {
                    "type": "Property",
                    "value": item.get('name', 'Unknown')
                },
                "mass": {
                    "type": "Property",
                    "value": item.get('mass', 'Unknown')
                },
                "fall": {
                    "type": "Property",
                    "value": item.get('fall', 'Unknown')
                },
                "year": {
                    "type": "Property",
                    "value": item.get('year', 'Unknown')
                },
                "location": {
                    "type": "GeoProperty",
                    "value": {
                        "type": "Point",
                        "coordinates": [
                            float(item['geolocation']['longitude']), 
                            float(item['geolocation']['latitude'])
                        ]
                    }
                }
            }
            ngsi_entities.append(ngsi_entity)
    return ngsi_entities

def send_or_update_entity(entity):
    entity_id = entity['id']
    headers = {"Content-Type": "application/ld+json", "Accept": "application/ld+json"}
    get_response = requests.get(f"{ORION_URL}/{entity_id}", headers=headers)

    if get_response.status_code == 200:
        
        # update payload, 
        update_payload = {
            "@context": NGSI_LD_CONTEXT,
            "location": {
                "type": "GeoProperty",  
                "value": entity["location"]["value"] 
            }
        }
        
        if 'name' in json.loads(get_response.text):
            update_payload["name"] = entity["name"]
        
        update_headers = {"Content-Type": "application/ld+json"}

        update_response = requests.patch(f"{ORION_URL}/{entity_id}/attrs", 
                                         json=update_payload, headers=update_headers)

        if update_response.status_code not in [204, 200]:
            print(f"Error updating entity {entity_id}: {update_response.status_code}")
            print(f"Response: {update_response.text}")
        else:
            print(f"Successfully updated entity {entity_id}")

    elif get_response.status_code == 404:
        # The entity does not exist
        create_headers = {"Content-Type": "application/ld+json"}
        create_response = requests.post(ORION_URL, json=entity, headers=create_headers)
        if create_response.status_code not in [201, 204]:
            print(f"Error creating entity {entity_id}: {create_response.status_code}")
            print(f"Response: {create_response.text}")
        else:
            print(f"Successfully created entity {entity_id}")
    else:
        print(f"Unexpected status code {get_response.status_code} when checking entity existence: {get_response.text}")

def send_to_orion(ngsi_data):
    for entity in ngsi_data:
        send_or_update_entity(entity)

def fetch_and_send_data_to_orion():
    while True:
        nasa_data = fetch_nasa_data()
        ngsi_data = transform_to_ngsi(nasa_data)
        send_to_orion(ngsi_data)
        time.sleep(3600)  # Fetch data every hour


threading.Thread(target=fetch_and_send_data_to_orion, daemon=True).start()

#server
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        url = urlparse(self.path)

        if url.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'rb') as file:
                self.wfile.write(file.read())

        elif url.path == '/data':
            self.send_response(200)
            self._set_headers()
            data = fetch_data_from_orion(ORION_URL)
            print("Data fetched from Orion:", data)  # Log the data
            self.wfile.write(json.dumps(data).encode())

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self._set_headers()

if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print('Starting server at http://localhost:8000')
    httpd.serve_forever()