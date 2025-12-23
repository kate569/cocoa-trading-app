#!/usr/bin/env python3
"""Fetch historical weather data for locations from Open-Meteo Archive API."""

import json
from datetime import date, timedelta
import requests


def load_locations(filepath="locations.json"):
    """Load location data from JSON file."""
    with open(filepath, "r") as f:
        return json.load(f)


def fetch_historical_weather(lat, lon, target_date):
    """Fetch historical precipitation from Open-Meteo Archive API."""
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": target_date.isoformat(),
        "end_date": target_date.isoformat(),
        "daily": "precipitation_sum"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def main():
    locations = load_locations()
    
    # Calculate date 7 days ago
    target_date = date.today() - timedelta(days=7)
    
    for name, coords in locations.items():
        lat = coords["lat"]
        lon = coords["lon"]
        
        weather = fetch_historical_weather(lat, lon, target_date)
        daily = weather["daily"]
        
        rainfall = daily["precipitation_sum"][0]
        date_str = daily["time"][0]
        
        # Format location name nicely (replace underscores, title case)
        display_name = name.replace("_", " ").title()
        
        print(f"{display_name} Rainfall on {date_str}: {rainfall} mm")


if __name__ == "__main__":
    main()
