import requests

from app.settings import ORS_API_KEY


def get_route_from_ors(origin_lat, origin_lng, dest_lat, dest_lng):
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {"Authorization": ORS_API_KEY, "Content-Type": "application/json"}

    body = {
        "coordinates": [
            [float(origin_lng), float(origin_lat)],
            [float(dest_lng), float(dest_lat)],
        ],
        "instructions": False,
    }

    response = requests.post(url, json=body, headers=headers)

    try:
        data = response.json()
    except ValueError:
        return {"error": "Invalid JSON from ORS"}

    if response.status_code != 200:
        return {"error": data.get("error", {}).get("message", response.text)}

    routes = data.get("routes")
    if not routes:
        return {"error": "No route found"}

    summary = routes[0]["summary"]

    return {
        "distance_meters": int(summary["distance"]),
        "duration_seconds": int(summary["duration"]),
    }
