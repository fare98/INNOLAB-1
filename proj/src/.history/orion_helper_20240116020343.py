import requests

def fetch_data_from_orion(orion_url):
    try:
        response = requests.get(orion_url)
        response.raise_for_status()
        data = response.json()

        processed_data = []
        for item in data:
            # Extract coordinates and check if they are valid
            coordinates = item.get("location", {}).get("coordinates", [])
            if len(coordinates) == 2:
                processed_data.append({
                    "name": item.get("name", {}).get("value", "Unknown"),
                    "latitude": coordinates[1],
                    "longitude": coordinates[0],
                    "url": item.get("url", {}).get("value", "#")
                })
        return processed_data
    except requests.RequestException as e:
        print(f"Error fetching data from Orion: {e}")
        return []
