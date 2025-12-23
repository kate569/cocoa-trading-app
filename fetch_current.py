#!/usr/bin/env python3
"""Fetch current weather data for locations from Open-Meteo API."""

import json
import requests


def load_locations(filepath="locations.json"):
    """Load location data from JSON file."""
    with open(filepath, "r") as f:
        return json.load(f)


def fetch_current_weather(lat, lon):
    """Fetch current temperature and precipitation from Open-Meteo API."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,precipitation"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def main():
    locations = load_locations()
    
    for name, coords in locations.items():
        lat = coords["lat"]
        lon = coords["lon"]
        
        weather = fetch_current_weather(lat, lon)
        current = weather["current"]
        
        temp = current["temperature_2m"]
        precip = current["precipitation"]
        
        # Format location name nicely (replace underscores, title case)
        display_name = name.replace("_", " ").title()
        
        print(f"{display_name} Status: {temp}°C, Precipitation: {precip}mm")


if __name__ == "__main__":
    main()
