import requests
import schedule
import time

NASA_API_URL = "https://data.nasa.gov/resource/gh4g-9sfh.json"
ORION_URL = "http://localhost:1026/v2/entities"

def fetch_nasa_data():
    response = requests.get(NASA_API_URL)
    data = response.json()
    return data

def transform_to_ngsi(nasa_data):
    ngsi_entities = []
    for item in nasa_data:
        entity = {
            "id": "urn:ngsi-ld:Asteroid:" + item['id'],
            "type": "Asteroid",
            "name": {
                "type": "Text",
                "value": item.get('name', 'Unknown')
            },
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "Point",
                    "coordinates": [float(item['geolocation']['longitude']), float(item['geolocation']['latitude'])]
                }
            }
        }
        ngsi_entities.append(entity)
    return ngsi_entities

def send_to_orion(ngsi_data):
    headers = {"Content-Type": "application/json"}
    for entity in ngsi_data:
        response = requests.post(ORION_URL, json=entity, headers=headers)
        if response.status_code not in [200, 201, 204]:
            print(f"Error sending data to Orion: {response.text}")

def job():
    nasa_data = fetch_nasa_data()
    ngsi_data = transform_to_ngsi(nasa_data)
    send_to_orion(ngsi_data)

# Schedule the job every hour (or choose a different interval)
schedule.every(1).hour.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
