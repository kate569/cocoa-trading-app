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
    
    # Years to fetch for 5-year baseline
    years = [2021, 2022, 2023, 2024, 2025]
    
    for name, coords in locations.items():
        lat = coords["lat"]
        lon = coords["lon"]
        
        # Fetch rainfall for each year in the 5-year window
        yearly_rainfall = {}
        for year in years:
            start_date = start_date_current.replace(year=year)
            end_date = end_date_current.replace(year=year)
            
            weather = fetch_historical_weather(lat, lon, start_date, end_date)
            total = calculate_total_rainfall(weather)
            yearly_rainfall[year] = total
        
        # Get values as list and calculate statistics
        rainfall_values = list(yearly_rainfall.values())
        current_rainfall = yearly_rainfall[2025]
        average_rainfall = sum(rainfall_values) / len(rainfall_values)
        deviation = current_rainfall - average_rainfall
        
        # Format location name nicely (replace underscores, title case)
        display_name = name.replace("_", " ").title()
        
        print(f"{display_name} 5-Year Analysis:")
        print(f"  5-Year Rainfall History: {rainfall_values}")
        print(f"  5-Year Average: {average_rainfall:.1f} mm")
        print(f"  Current Deviation from Average: {deviation:.1f} mm")


if __name__ == "__main__":
    main()
