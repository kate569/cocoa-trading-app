#!/usr/bin/env python3
"""Check cocoa market fundamentals and calculate position size multiplier."""

import json


def load_fundamentals(filepath="fundamentals.json"):
    """Load fundamentals data from JSON file."""
    with open(filepath, "r") as f:
        return json.load(f)


def calculate_position_multiplier(stocks_ratio):
    """Calculate position size multiplier based on stocks-to-usage ratio."""
    if stocks_ratio < 30:
        return 2.5, "⚠️ CRITICAL DEFICIT"
    elif stocks_ratio < 35:
        return 2.0, "🟠 LOW STOCKS"
    else:
        return 1.0, "✅ STOCKS HEALTHY"


def get_fundamental_multiplier():
    """
    Get the position size multiplier based on market fundamentals.
    
    Returns:
        float: Position size multiplier (1.0, 2.0, or 2.5)
    """
    fundamentals = load_fundamentals()
    stocks_ratio = fundamentals["global_stocks_to_usage_ratio"]
    multiplier, _ = calculate_position_multiplier(stocks_ratio)
    return multiplier


def get_fundamentals_analysis():
    """
    Get full fundamentals analysis including ratio, multiplier, and status.
    
    Returns:
        dict: {"stocks_ratio": float, "multiplier": float, "status": str, "status_display": str}
    """
    fundamentals = load_fundamentals()
    stocks_ratio = fundamentals["global_stocks_to_usage_ratio"]
    multiplier, status_display = calculate_position_multiplier(stocks_ratio)
    
    if multiplier == 2.5:
        status = "CRITICAL_DEFICIT"
    elif multiplier == 2.0:
        status = "LOW_STOCKS"
    else:
        status = "HEALTHY"
    
    return {
        "stocks_ratio": stocks_ratio,
        "multiplier": multiplier,
        "status": status,
        "status_display": status_display
    }


def main():
    print("📊 Cocoa Market Fundamentals Check")
    print("-" * 40)
    
    analysis = get_fundamentals_analysis()
    
    print(f"Global Stocks-to-Usage Ratio: {analysis['stocks_ratio']}%")
    print()
    print(f"{analysis['status_display']}: Position Size Multiplier = {analysis['multiplier']}x")


if __name__ == "__main__":
    main()
