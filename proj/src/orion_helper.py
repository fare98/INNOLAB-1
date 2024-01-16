import requests

def fetch_data_from_orion(orion_url):
    try:
        headers = {"Accept": "application/ld+json"}
        params = {"type": "Asteroid"}
        response = requests.get(orion_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        processed_data = []
        for item in data:
            coordinates = item.get("location", {}).get("value", {}).get("coordinates", [])
            if len(coordinates) == 2:
                processed_data.append({
                    "name": item.get("https://uri.etsi.org/ngsi-ld/name", {}).get("value", "Unknown"),
                    "latitude": coordinates[1],
                    "longitude": coordinates[0],
                     
                })
        return processed_data
    except requests.RequestException as e:
        print(f"Error fetching data from Orion: {e}")
        return []