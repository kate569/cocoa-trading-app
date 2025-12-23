#!/usr/bin/env python3
"""Fetch ENSO/ONI (Oceanic Niño Index) data from NOAA."""

import requests


def fetch_oni_data():
    """Fetch ONI data from NOAA PSL."""
    url = "https://psl.noaa.gov/data/correlation/oni.data"
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def parse_oni_data(data_text):
    """Parse ONI data and find the most recent valid value."""
    lines = data_text.strip().split('\n')
    
    latest_value = None
    latest_year = None
    latest_month = None
    
    # Month names for display
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    for line in lines:
        parts = line.split()
        
        # Skip lines that don't start with a year (header, footer, etc.)
        if not parts or not parts[0].isdigit():
            continue
        
        # Skip the header line (just two numbers: start_year end_year)
        if len(parts) == 2:
            continue
        
        year = int(parts[0])
        
        # Parse monthly values (columns 1-12)
        for month_idx, value_str in enumerate(parts[1:13]):
            try:
                value = float(value_str)
                # Skip missing data indicator (-99.9 or -99.90)
                if value < -90:
                    continue
                # Update latest value
                latest_value = value
                latest_year = year
                latest_month = month_idx
            except ValueError:
                continue
    
    return latest_value, latest_year, month_names[latest_month] if latest_month is not None else None


def interpret_oni(value):
    """Interpret ONI value according to trading strategy."""
    if value > 1.2:
        return "BULLISH", "🌊 EL NIÑO SIGNAL: STRONG BULLISH (Lead time 6-8 mo)"
    elif value < -1.0:
        return "BEARISH", "❄️ LA NIÑA SIGNAL: Check Atlantic Temps"
    else:
        return "NEUTRAL", "⚪ ENSO Neutral"


def get_enso_signal():
    """
    Get ENSO/ONI signal for trading strategy.
    
    Returns:
        dict: {"value": float, "signal": "BULLISH/NEUTRAL/BEARISH", 
               "month": str, "year": int, "display": str}
    """
    data_text = fetch_oni_data()
    oni_value, year, month = parse_oni_data(data_text)
    
    if oni_value is not None:
        signal, display = interpret_oni(oni_value)
        return {
            "value": oni_value,
            "signal": signal,
            "month": month,
            "year": year,
            "display": display
        }
    else:
        return {
            "value": None,
            "signal": "UNKNOWN",
            "month": None,
            "year": None,
            "display": "Error: Could not parse ONI data"
        }


def main():
    print("Fetching ENSO/ONI data from NOAA...\n")
    
    result = get_enso_signal()
    
    if result["value"] is not None:
        print(f"Latest ONI Value: {result['value']:.2f} ({result['month']} {result['year']})")
        print(result["display"])
    else:
        print(result["display"])


if __name__ == "__main__":
    main()
