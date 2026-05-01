import os
import urllib.parse
import requests

def generate_maps_link(location: str) -> str:
    """Generates a Google Maps search link for a given location."""
    if not location:
        return ""
        
    encoded_location = urllib.parse.quote(location)
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    
    if api_key:
        try:
            url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_location}&key={api_key}"
            response = requests.get(url, timeout=1.0)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "OK" and data.get("results"):
                    lat = data["results"][0]["geometry"]["location"]["lat"]
                    lng = data["results"][0]["geometry"]["location"]["lng"]
                    return f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
        except Exception:
            # Silently fallback to simple link on any error (timeout, network, parsing, etc.)
            pass
            
    return f"https://www.google.com/maps/search/?api=1&query={encoded_location}"
