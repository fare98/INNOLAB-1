import req

def fetch_data_from_orion(orion_url):
    """
    Fetch data from Orion Context Broker.
    
    Args:
        orion_url (str): URL of the Orion Context Broker instance

    Returns:
        list: A list of processed data suitable for the front-end
    """
    try:
        response = requests.get(orion_url)
        response.raise_for_status()
        data = response.json()

        processed_data = []
        for item in data:
            processed_data.append({
                "name": item.get("name", {}).get("value", "Unknown"),
                "latitude": item.get("location", {}).get("coordinates", [])[1],
                "longitude": item.get("location", {}).get("coordinates", [])[0],
                "url": item.get("url", {}).get("value", "#")
            })

        return processed_data
    except requests.RequestException as e:
        print(f"Error fetching data from Orion: {e}")
        return []
