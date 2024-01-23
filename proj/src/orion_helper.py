import requests

def fetch_data_from_orion(orion_url):
    try:
        headers = {"Accept": "application/ld+json"}
        processed_data = []
        page = 0
        page_size = 20  # Orion's default page size is 20
        total_fetched = 0
        
        
        while True:
            params = {"type": "Asteroid", "limit": page_size, "offset": page * page_size}
            response = requests.get(orion_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            
            if not data:
                break  
            
            
            for item in data:
                coordinates = item.get("location", {}).get("value", {}).get("coordinates", [])
                if len(coordinates) == 2:
                    processed_data.append({
                        "name": item.get("https://uri.etsi.org/ngsi-ld/name", {}).get("value", "Unknown"),
                        "latitude": coordinates[1],
                        "longitude": coordinates[0],
                        "mass": item.get("mass", {}).get("value", 0),
                        "fall": item.get("fall", {}).get("value", "Unknown"),
                        "year": item.get("year", {}).get("value", "Unknown")
                    })
            
            total_fetched += len(data)
            if len(data) < page_size:
                break  
            page += 1  

        return processed_data
    except requests.RequestException as e:
        print(f"Error fetching data from Orion: {e}")
        return []
