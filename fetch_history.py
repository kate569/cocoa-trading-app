#!/usr/bin/env python3
"""Fetch historical weather data for locations from Open-Meteo Archive API."""

import json
from datetime import date, timedelta
import requests


def load_locations(filepath="locations.json"):
    """Load location data from JSON file."""
    with open(filepath, "r") as f:
        return json.load(f)


def fetch_historical_weather(lat, lon, start_date, end_date):
    """Fetch historical precipitation from Open-Meteo Archive API."""
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "daily": "precipitation_sum"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def main():
    locations = load_locations()
    
    # Calculate date range for last 30 days
    end_date = date.today() - timedelta(days=1)  # Yesterday (most recent complete day)
    start_date = end_date - timedelta(days=29)   # 30 days total
    
    for name, coords in locations.items():
        lat = coords["lat"]
        lon = coords["lon"]
        
        weather = fetch_historical_weather(lat, lon, start_date, end_date)
        daily = weather["daily"]
        
        # Calculate total rainfall, handling None values
        precipitation_values = daily["precipitation_sum"]
        total_rainfall = sum(v for v in precipitation_values if v is not None)
        
        # Format location name nicely (replace underscores, title case)
        display_name = name.replace("_", " ").title()
        
        print(f"{display_name} Total Rainfall (Last 30 Days): {total_rainfall} mm")


if __name__ == "__main__":
    main()
