from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import requests
from urllib.parse import urlparse
import threading
import time
from orion_helper import fetch_data_from_orion


# NASA to Orion integration
NASA_API_URL = "https://data.nasa.gov/resource/gh4g-9sfh.json"
ORION_URL = "http://localhost:1026/v2/entities"

def fetch_nasa_data():
    response = requests.get(NASA_API_URL)
    return response.json()

def transform_to_ngsi(nasa_data):
    ngsi_entities = []
    for item in nasa_data:
        if 'geolocation' in item and 'latitude' in item['geolocation'] and 'longitude' in item['geolocation']:
            # Construct the NGSI entity without the 'id' and 'type' in the attributes
            entity_attributes = {
                "name": {
                    "type": "Text",
                    "value": item.get('name', 'Unknown')
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
                # Add other attributes here if necessary
            }
            # The NGSI entity with 'id' and 'type' included separately
            ngsi_entity = {
                "id": f"urn:ngsi-ld:Asteroid:{item['id']}",
                "type": "Asteroid",
                "attributes": entity_attributes
            }
            ngsi_entities.append(ngsi_entity)
    return ngsi_entities


def send_or_update_entity(entity):
    entity_id = entity['id']
    headers = {"Accept": "application/json"}  # Only Accept header is needed for GET
    get_response = requests.get(f"{ORION_URL}/{entity_id}", headers=headers)
    
    if get_response.status_code == 200:
        # The entity already exists, so we update it
        update_headers = {"Content-Type": "application/json"}
        update_response = requests.patch(f"{ORION_URL}/{entity_id}/attrs", json=entity, headers=update_headers)
        if update_response.status_code not in [204, 200]:
            print(f"Error updating entity {entity_id}: {update_response.json()}")
        else:
            print(f"Successfully updated entity {entity_id}")
    elif get_response.status_code == 404:
        # The entity does not exist, so we create it
        create_headers = {"Content-Type": "application/json"}
        create_response = requests.post(ORION_URL, json=entity, headers=create_headers)
        if create_response.status_code not in [201, 204]:
            print(f"Error creating entity {entity_id}: {create_response.json()}")
        else:
            print(f"Successfully created entity {entity_id}")
    else:
        print(f"Error checking existence of entity {entity_id}: {get_response.json()}")


def send_to_orion(ngsi_data):
    for entity in ngsi_data:
        send_or_update_entity(entity)



def fetch_and_send_data_to_orion():
    while True:
        nasa_data = fetch_nasa_data()
        ngsi_data = transform_to_ngsi(nasa_data)
        send_to_orion(ngsi_data)
        time.sleep(3600)  # Fetch data every hour, adjust as needed

# Start the data fetching in a separate thread
threading.Thread(target=fetch_and_send_data_to_orion, daemon=True).start()

# HTTP server part
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
            orion_url = 'http://localhost:1026/v2/entities'
            data = fetch_data_from_orion(orion_url)
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
