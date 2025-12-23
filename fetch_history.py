#!/usr/bin/env python3
"""Fetch historical weather data for locations from Open-Meteo Archive API."""

import json
import statistics
from datetime import date, timedelta
import requests


def load_locations(filepath="locations.json"):
    """Load location data from JSON file."""
    with open(filepath, "r") as f:
        return json.load(f)


def fetch_historical_weather(lat, lon, start_date, end_date):
    """Fetch historical weather data from Open-Meteo Archive API."""
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "daily": "precipitation_sum,temperature_2m_max,wind_speed_10m_max,relative_humidity_2m_mean"
    }
    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()
    return response.json()


def calculate_total_rainfall(weather_data):
    """Calculate total rainfall from weather data, handling None values."""
    precipitation_values = weather_data["daily"]["precipitation_sum"]
    return sum(v for v in precipitation_values if v is not None)


def analyze_weather():
    """
    Analyze weather data for all locations.
    
    Returns:
        dict: Analysis results containing status for each region and alerts.
    """
    locations = load_locations()
    
    # Calculate date range for last 30 days (current year)
    end_date_current = date.today() - timedelta(days=1)
    start_date_current = end_date_current - timedelta(days=29)
    
    # Years to fetch for 5-year baseline
    years = [2021, 2022, 2023, 2024, 2025]
    
    # Results dictionary
    results = {
        "regions": {},
        "severe_drought_regions": [],
        "dual_region_drought_detected": False
    }
    
    for name, coords in locations.items():
        lat = coords["lat"]
        lon = coords["lon"]
        display_name = name.replace("_", " ").title()
        
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
        average_rainfall = statistics.mean(rainfall_values)
        std_deviation = statistics.stdev(rainfall_values)
        deviation = current_rainfall - average_rainfall
        
        # Calculate Z-Score (Simplified SPI)
        z_score = (current_rainfall - average_rainfall) / std_deviation
        
        # Determine drought status based on Z-Score
        if z_score < -1.5:
            drought_status = "Severe Drought"
            drought_status_display = "🔴 SEVERE DROUGHT ALERT"
            results["severe_drought_regions"].append(display_name)
        elif z_score < -1.0:
            drought_status = "Dry Warning"
            drought_status_display = "🟠 DRY WARNING"
        else:
            drought_status = "Normal"
            drought_status_display = "💧 Moisture OK"
        
        # Fetch current period weather for temperature analysis
        current_weather = fetch_historical_weather(lat, lon, start_date_current, end_date_current)
        temp_max_values = current_weather["daily"]["temperature_2m_max"]
        
        # Calculate temperature statistics (handling None values)
        valid_temps = [t for t in temp_max_values if t is not None]
        avg_max_temp = statistics.mean(valid_temps) if valid_temps else 0
        days_above_32 = sum(1 for t in valid_temps if t > 32.0)
        
        # Determine heat stress status
        if days_above_32 >= 7:
            heat_status = "Critical Heat"
            heat_status_display = "⚠️ CRITICAL HEAT ALERT"
        else:
            heat_status = "Normal"
            heat_status_display = "✅ Normal"
        
        # Calculate wind and humidity statistics for Harmattan detection
        wind_values = current_weather["daily"]["wind_speed_10m_max"]
        humidity_values = current_weather["daily"]["relative_humidity_2m_mean"]
        
        valid_wind = [w for w in wind_values if w is not None]
        valid_humidity = [h for h in humidity_values if h is not None]
        
        avg_wind_speed = statistics.mean(valid_wind) if valid_wind else 0
        avg_humidity = statistics.mean(valid_humidity) if valid_humidity else 100
        
        # Harmattan check: 25 knots ≈ 46 km/h, low humidity < 40%
        if avg_wind_speed > 46 and avg_humidity < 40:
            harmattan_status = "Harmattan Active"
            harmattan_status_display = "🌪️ HARMATTAN ALERT"
        else:
            harmattan_status = "Normal"
            harmattan_status_display = "🍃 Wind Normal"
        
        # Store region data
        results["regions"][display_name] = {
            "drought_status": drought_status,
            "drought_status_display": drought_status_display,
            "heat_status": heat_status,
            "heat_status_display": heat_status_display,
            "harmattan_status": harmattan_status,
            "harmattan_status_display": harmattan_status_display,
            "z_score": z_score,
            "rainfall_values": rainfall_values,
            "average_rainfall": average_rainfall,
            "current_rainfall": current_rainfall,
            "deviation": deviation,
            "std_deviation": std_deviation,
            "avg_max_temp": avg_max_temp,
            "days_above_32": days_above_32,
            "avg_wind_speed": avg_wind_speed,
            "avg_humidity": avg_humidity
        }
    
    # Check for dual-region drought
    results["dual_region_drought_detected"] = len(results["severe_drought_regions"]) >= 2
    
    return results


def print_analysis(results):
    """Print analysis results to console."""
    for region_name, data in results["regions"].items():
        print(f"{region_name} 5-Year Analysis: {data['heat_status_display']}")
        print(f"  5-Year Rainfall History: {data['rainfall_values']}")
        print(f"  5-Year Average: {data['average_rainfall']:.1f} mm")
        print(f"  Current Deviation from Average: {data['deviation']:.1f} mm")
        print(f"  Standard Deviation: {data['std_deviation']:.1f}")
        print(f"  Z-Score (SPI proxy): {data['z_score']:.2f}")
        print(f"  Drought Status: {data['drought_status_display']}")
        print(f"  Avg Max Temp: {data['avg_max_temp']:.1f} °C")
        print(f"  Days > 32°C: {data['days_above_32']}")
        print(f"  Avg Wind Speed: {data['avg_wind_speed']:.1f} km/h")
        print(f"  Avg Humidity: {data['avg_humidity']:.1f}%")
        print(f"  Harmattan Status: {data['harmattan_status_display']}")
        print()
    
    # Dual-region drought check
    if results["dual_region_drought_detected"]:
        print("🚨🚨🚨 MARKET ALERT: DUAL-REGION SUPPLY SHOCK DETECTED! (High Conviction Buy)")
    else:
        print("No dual-region drought currently detected.")


def main():
    """Main function to run weather analysis."""
    results = analyze_weather()
    print_analysis(results)
    return results


if __name__ == "__main__":
    main()
