#!/usr/bin/env python3
"""Fetch ICE Cocoa Futures market data using yfinance."""

import yfinance as yf


def fetch_cocoa_futures():
    """Fetch current cocoa futures data."""
    ticker = yf.Ticker("CC=F")
    
    # Get current market data
    info = ticker.info
    
    # Get current price and previous close
    current_price = info.get("regularMarketPrice") or info.get("previousClose")
    previous_close = info.get("regularMarketPreviousClose") or info.get("previousClose")
    
    # If regularMarketPrice not available, try getting from history
    if current_price is None:
        hist = ticker.history(period="2d")
        if len(hist) >= 1:
            current_price = hist["Close"].iloc[-1]
        if len(hist) >= 2:
            previous_close = hist["Close"].iloc[-2]
    
    return current_price, previous_close


def get_market_data():
    """
    Get current cocoa futures market data.
    
    Returns:
        dict: {"price": float, "change_pct": float, "previous_close": float}
    """
    current_price, previous_close = fetch_cocoa_futures()
    
    change_pct = None
    if current_price is not None and previous_close is not None and previous_close != 0:
        change_pct = ((current_price - previous_close) / previous_close) * 100
    
    return {
        "price": current_price,
        "change_pct": change_pct,
        "previous_close": previous_close
    }


def main():
    print("🍫 ICE Cocoa Futures (CC=F)")
    print("-" * 30)
    
    data = get_market_data()
    
    if data["price"] is not None:
        print(f"Current Price: ${data['price']:,.2f}")
        
        if data["change_pct"] is not None:
            change_symbol = "+" if data["change_pct"] >= 0 else ""
            print(f"Previous Close: ${data['previous_close']:,.2f}")
            print(f"Daily Change: {change_symbol}{data['change_pct']:.2f}%")
        else:
            print("Daily Change: N/A")
    else:
        print("Error: Could not fetch price data")


if __name__ == "__main__":
    main()
