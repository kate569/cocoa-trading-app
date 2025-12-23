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


def main():
    print("🍫 ICE Cocoa Futures (CC=F)")
    print("-" * 30)
    
    current_price, previous_close = fetch_cocoa_futures()
    
    if current_price is not None:
        print(f"Current Price: ${current_price:,.2f}")
        
        if previous_close is not None and previous_close != 0:
            daily_change = ((current_price - previous_close) / previous_close) * 100
            change_symbol = "+" if daily_change >= 0 else ""
            print(f"Previous Close: ${previous_close:,.2f}")
            print(f"Daily Change: {change_symbol}{daily_change:.2f}%")
        else:
            print("Daily Change: N/A")
    else:
        print("Error: Could not fetch price data")


if __name__ == "__main__":
    main()
