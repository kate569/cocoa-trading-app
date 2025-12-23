#!/usr/bin/env python3
"""
Generate candlestick chart with SMA-50 overlay for Cocoa Futures.
Saves chart as docs/chart.png for dashboard display.
"""

import os
import yfinance as yf
import mplfinance as mpf
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server


def generate_chart(output_path="docs/chart.png"):
    """
    Generate a candlestick chart with SMA-50 overlay.
    
    Args:
        output_path: Path to save the chart image
    
    Returns:
        str: Path to the saved chart
    """
    print("Fetching 6 months of historical data for CC=F...")
    
    # Fetch 6 months of historical data
    ticker = yf.Ticker("CC=F")
    hist = ticker.history(period="6mo")
    
    if hist.empty:
        print("Error: No historical data available")
        return None
    
    # Calculate SMA-50
    hist['SMA50'] = hist['Close'].rolling(window=50).mean()
    
    # Create custom market colors for dark theme
    mc = mpf.make_marketcolors(
        up='#00ff88',      # Green for up candles
        down='#ff4444',    # Red for down candles
        edge='inherit',
        wick='inherit',
        volume='in',
        ohlc='i'
    )
    
    # Create custom style matching our dashboard dark theme
    style = mpf.make_mpf_style(
        base_mpf_style='nightclouds',
        marketcolors=mc,
        figcolor='#0a0a0a',
        facecolor='#111111',
        edgecolor='#333333',
        gridcolor='#222222',
        gridstyle='-',
        gridaxis='both',
        y_on_right=True,
        rc={
            'font.size': 10,
            'axes.labelcolor': '#888888',
            'axes.titlesize': 14,
            'xtick.color': '#888888',
            'ytick.color': '#888888',
            'text.color': '#00ff88',
        }
    )
    
    # Create SMA plot configuration
    sma_plot = mpf.make_addplot(
        hist['SMA50'],
        color='#00aaff',
        width=1.5,
        label='SMA 50'
    )
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Create the chart
    print(f"Generating candlestick chart...")
    
    mpf.plot(
        hist,
        type='candle',
        style=style,
        title='\nICE Cocoa Futures (CC=F) - 6 Month Chart',
        ylabel='Price (USD)',
        volume=True,
        ylabel_lower='Volume',
        addplot=sma_plot,
        figsize=(12, 8),
        savefig=dict(
            fname=output_path,
            dpi=150,
            bbox_inches='tight',
            facecolor='#0a0a0a',
            edgecolor='none'
        ),
        tight_layout=True
    )
    
    print(f"Chart saved to: {output_path}")
    return output_path


def main():
    """Generate the chart."""
    chart_path = generate_chart()
    if chart_path:
        print(f"✅ Chart successfully generated: {chart_path}")
    else:
        print("❌ Failed to generate chart")


if __name__ == "__main__":
    main()
