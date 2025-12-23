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


def main():
    print("📊 Cocoa Market Fundamentals Check")
    print("-" * 40)
    
    fundamentals = load_fundamentals()
    stocks_ratio = fundamentals["global_stocks_to_usage_ratio"]
    
    print(f"Global Stocks-to-Usage Ratio: {stocks_ratio}%")
    print()
    
    multiplier, status = calculate_position_multiplier(stocks_ratio)
    
    print(f"{status}: Position Size Multiplier = {multiplier}x")


if __name__ == "__main__":
    main()
