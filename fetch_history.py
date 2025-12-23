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


def calculate_total_rainfall(weather_data):
    """Calculate total rainfall from weather data, handling None values."""
    precipitation_values = weather_data["daily"]["precipitation_sum"]
    return sum(v for v in precipitation_values if v is not None)


def main():
    locations = load_locations()
    
    # Calculate date range for last 30 days (current year)
    end_date_current = date.today() - timedelta(days=1)  # Yesterday (most recent complete day)
    start_date_current = end_date_current - timedelta(days=29)   # 30 days total
    
    # Calculate same 30-day window from previous year
    end_date_previous = end_date_current.replace(year=end_date_current.year - 1)
    start_date_previous = start_date_current.replace(year=start_date_current.year - 1)
    
    for name, coords in locations.items():
        lat = coords["lat"]
        lon = coords["lon"]
        
        # Fetch current year data
        weather_current = fetch_historical_weather(lat, lon, start_date_current, end_date_current)
        total_current = calculate_total_rainfall(weather_current)
        
        # Fetch previous year data
        weather_previous = fetch_historical_weather(lat, lon, start_date_previous, end_date_previous)
        total_previous = calculate_total_rainfall(weather_previous)
        
        # Calculate difference
        difference = total_current - total_previous
        
        # Format location name nicely (replace underscores, title case)
        display_name = name.replace("_", " ").title()
        
        print(f"{display_name} Year-over-Year Comparison:")
        print(f"  Current 30-Day Sum: {total_current} mm")
        print(f"  Previous Year 30-Day Sum: {total_previous} mm")
        print(f"  Difference: {difference} mm")


if __name__ == "__main__":
    main()
