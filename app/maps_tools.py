# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google Maps Geocoding and Places (New) API tools."""

import os
from urllib.parse import quote

import requests


def geocode_address(address: str) -> str:
    """Converts a street address or location name into geographic coordinates (latitude and longitude).

    Args:
        address: The address or location name to geocode (e.g., '1600 Amphitheatre Pkwy, Mountain View, CA').

    Returns:
        Formatted summary with address, latitude, and longitude.
    """
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    if not api_key or api_key == "PASTE_KEY_HERE":
        return "Error: GOOGLE_MAPS_API_KEY environment variable is not configured with a valid API key."

    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={quote(address)}&key={api_key}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        status = data.get("status")
        if status != "OK" or not data.get("results"):
            return f"Geocoding failed for address '{address}': {status or 'No results found.'}"

        result = data["results"][0]
        formatted_address = result.get("formatted_address", address)
        location = result.get("geometry", {}).get("location", {})
        lat = location.get("lat")
        lng = location.get("lng")

        return (
            f"Geocoding Result for '{address}':\n"
            f"- Formatted Address: {formatted_address}\n"
            f"- Location: Latitude {lat}, Longitude {lng}"
        )
    except Exception as e:
        return f"Error executing Geocoding request for '{address}': {e}"


def find_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "florist",
    radius_meters: float = 5000.0,
) -> str:
    """Finds nearby places (e.g., florists, plant nurseries, garden centers) using the Google Places API (New).

    Args:
        latitude: Center latitude coordinate.
        longitude: Center longitude coordinate.
        place_type: Type of place to search for (e.g., 'florist', 'garden_center', 'store').
        radius_meters: Search radius in meters (default 5000.0 meters / ~5 km).

    Returns:
        Formatted list of matching nearby places with name, formatted address, and coordinates.
    """
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    if not api_key or api_key == "PASTE_KEY_HERE":
        return "Error: GOOGLE_MAPS_API_KEY environment variable is not configured with a valid API key."

    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location",
    }
    payload = {
        "includedTypes": [place_type],
        "locationRestriction": {
            "circle": {
                "center": {"latitude": latitude, "longitude": longitude},
                "radius": radius_meters,
            }
        },
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()

        places = data.get("places", [])
        if not places:
            return f"No nearby places of type '{place_type}' found within {radius_meters}m of ({latitude}, {longitude})."

        results_summary = []
        for p in places[:5]:
            display_name = p.get("displayName", {}).get("text", "Unknown Name")
            formatted_address = p.get("formattedAddress", "No address provided")
            loc = p.get("location", {})
            plat = loc.get("latitude")
            plng = loc.get("longitude")

            results_summary.append(
                f"- Name: {display_name}\n"
                f"  Address: {formatted_address}\n"
                f"  Location: ({plat}, {plng})"
            )

        return (
            f"Nearby '{place_type}' Search Results near ({latitude}, {longitude}):\n"
            + "\n".join(results_summary)
        )
    except Exception as e:
        return f"Error executing Places (New) search: {e}"
