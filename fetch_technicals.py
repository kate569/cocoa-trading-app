#!/usr/bin/env python3
"""
Technical Analysis for Cocoa Futures.
Calculates SMA_50 and RSI_14 indicators.
"""

import yfinance as yf
import pandas as pd


def calculate_rsi(prices, period=14):
    """
    Calculate Relative Strength Index (RSI).
    
    Args:
        prices: Pandas Series of closing prices
        period: RSI period (default 14)
    
    Returns:
        float: Latest RSI value
    """
    # Calculate price changes
    delta = prices.diff()
    
    # Separate gains and losses
    gains = delta.where(delta > 0, 0)
    losses = (-delta).where(delta < 0, 0)
    
    # Calculate average gains and losses using exponential moving average
    avg_gains = gains.rolling(window=period, min_periods=period).mean()
    avg_losses = losses.rolling(window=period, min_periods=period).mean()
    
    # Calculate RS and RSI
    rs = avg_gains / avg_losses
    rsi = 100 - (100 / (1 + rs))
    
    return rsi.iloc[-1]


def calculate_sma(prices, period=50):
    """
    Calculate Simple Moving Average (SMA).
    
    Args:
        prices: Pandas Series of closing prices
        period: SMA period (default 50)
    
    Returns:
        float: Latest SMA value
    """
    sma = prices.rolling(window=period, min_periods=period).mean()
    return sma.iloc[-1]


def get_technical_analysis():
    """
    Get technical analysis for Cocoa Futures (CC=F).
    
    Returns:
        dict: {
            "price": float,
            "rsi": float,
            "sma": float,
            "signal": "BUY/SELL/WAIT",
            "trend": str,
            "rsi_status": str,
            "explanation": str
        }
    """
    # Fetch 3 months of historical data
    ticker = yf.Ticker("CC=F")
    hist = ticker.history(period="3mo")
    
    if hist.empty or len(hist) < 50:
        return {
            "price": None,
            "rsi": None,
            "sma": None,
            "volume": 0,
            "signal": "UNKNOWN",
            "trend": "Unknown",
            "rsi_status": "Unknown",
            "explanation": "Insufficient data for analysis"
        }
    
    # Get closing prices and volume
    closes = hist["Close"]
    volumes = hist["Volume"]
    current_price = closes.iloc[-1]
    
    # Get latest volume (handle NaN)
    latest_volume = volumes.iloc[-1]
    if pd.isna(latest_volume):
        latest_volume = 0
    else:
        latest_volume = int(latest_volume)
    
    # Calculate indicators
    sma_50 = calculate_sma(closes, period=50)
    rsi_14 = calculate_rsi(closes, period=14)
    
    # Determine trend
    if current_price > sma_50:
        trend = "Uptrend"
        trend_display = "📈 Price is in an Uptrend"
    else:
        trend = "Downtrend"
        trend_display = "📉 Price is in a Downtrend"
    
    # Determine RSI status
    if rsi_14 > 70:
        rsi_status = "Overbought"
        rsi_display = "🔴 Market is Overbought (Risk of drop)"
    elif rsi_14 < 30:
        rsi_status = "Oversold"
        rsi_display = "🟢 Market is Oversold (Buying opportunity)"
    else:
        rsi_status = "Neutral"
        rsi_display = "⚪ RSI is Neutral"
    
    # Generate trading signal
    explanations = [trend_display, rsi_display]
    
    if trend == "Uptrend" and rsi_status == "Oversold":
        signal = "BUY"
        explanations.append("✅ STRONG BUY: Uptrend + Oversold dip")
    elif trend == "Uptrend" and rsi_status == "Neutral":
        signal = "BUY"
        explanations.append("✅ BUY: Price above SMA, momentum healthy")
    elif trend == "Uptrend" and rsi_status == "Overbought":
        signal = "WAIT"
        explanations.append("⏸️ WAIT: Uptrend but overbought, wait for pullback")
    elif trend == "Downtrend" and rsi_status == "Oversold":
        signal = "WAIT"
        explanations.append("⏸️ WAIT: Oversold but in downtrend, wait for reversal")
    elif trend == "Downtrend" and rsi_status == "Overbought":
        signal = "SELL"
        explanations.append("🔴 SELL: Downtrend + Overbought = bearish")
    else:
        signal = "WAIT"
        explanations.append("⏸️ WAIT: No clear signal")
    
    return {
        "price": float(current_price),
        "rsi": float(rsi_14),
        "sma": float(sma_50),
        "volume": latest_volume,
        "signal": signal,
        "trend": trend,
        "rsi_status": rsi_status,
        "trend_display": trend_display,
        "rsi_display": rsi_display,
        "explanation": " | ".join(explanations)
    }


def main():
    """Test the technical analysis function."""
    print("📊 Cocoa Futures Technical Analysis")
    print("=" * 50)
    
    result = get_technical_analysis()
    
    if result["price"]:
        print(f"\nCurrent Price: ${result['price']:,.2f}")
        print(f"SMA (50-day):  ${result['sma']:,.2f}")
        print(f"RSI (14-day):  {result['rsi']:.1f}")
        print(f"\nTrend:  {result['trend_display']}")
        print(f"RSI:    {result['rsi_display']}")
        print(f"\nSignal: {result['signal']}")
        print(f"\n{result['explanation']}")
    else:
        print(result["explanation"])


if __name__ == "__main__":
    main()
