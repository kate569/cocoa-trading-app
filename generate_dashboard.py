#!/usr/bin/env python3
"""
Generate HTML Dashboard for Cocoa Trading Intelligence.
Creates a dark-mode styled index.html with all trading signals.
"""

from datetime import datetime, timezone
from fetch_history import analyze_weather
from fetch_enso import get_enso_signal
from fetch_market import get_market_data
from check_fundamentals import get_fundamentals_analysis
from fetch_technicals import get_technical_analysis
from market_narrative import generate_market_narrative


def calculate_verdict(weather, enso, fundamentals):
    """Calculate the final trading verdict."""
    signals = []
    
    # Check for dual-region drought
    if weather["dual_region_drought_detected"]:
        signals.append(("EXTREME_BULLISH", "Dual-Region Drought"))
    
    # Check individual region alerts
    for region, data in weather["regions"].items():
        if data["drought_status"] == "Severe Drought":
            signals.append(("BULLISH", f"{region} Drought"))
        if data["heat_status"] == "Critical Heat":
            signals.append(("BULLISH", f"{region} Heat Stress"))
        if data["harmattan_status"] == "Harmattan Active":
            signals.append(("BULLISH", f"{region} Harmattan"))
    
    # Check ENSO
    if enso["signal"] == "BULLISH":
        signals.append(("BULLISH", "El Niño Active"))
    elif enso["signal"] == "BEARISH":
        signals.append(("BEARISH", "La Niña Active"))
    
    multiplier = fundamentals["multiplier"]
    
    bullish_count = sum(1 for s in signals if s[0] in ["BULLISH", "EXTREME_BULLISH"])
    extreme_count = sum(1 for s in signals if s[0] == "EXTREME_BULLISH")
    
    if extreme_count > 0:
        verdict = "🚨 MAXIMUM CONVICTION LONG"
        verdict_class = "verdict-extreme"
        description = "Dual-region supply shock detected"
    elif bullish_count >= 2:
        verdict = "🔥 HIGH CONVICTION LONG"
        verdict_class = "verdict-high"
        description = "Multiple bullish signals aligned"
    elif bullish_count == 1:
        verdict = "📈 MODERATE BULLISH"
        verdict_class = "verdict-moderate"
        description = "Single bullish signal active"
    else:
        verdict = "⚪ NEUTRAL - NO POSITION"
        verdict_class = "verdict-neutral"
        description = "Waiting for clearer signals"
    
    return verdict, verdict_class, description, multiplier, signals


def generate_html():
    """Generate the HTML dashboard."""
    print("Fetching data from all sources...")
    
    # Fetch all data
    weather = analyze_weather()
    enso = get_enso_signal()
    market = get_market_data()
    fundamentals = get_fundamentals_analysis()
    tech_data = get_technical_analysis()
    
    # Calculate verdict
    verdict, verdict_class, description, multiplier, active_signals = calculate_verdict(
        weather, enso, fundamentals
    )
    
    # Generate market narrative
    news_sentiment = fundamentals.get("news_sentiment", "NEUTRAL")
    narrative = generate_market_narrative(tech_data, fundamentals, weather, news_sentiment)
    
    # Format market change
    if market["change_pct"] is not None:
        change_class = "positive" if market["change_pct"] >= 0 else "negative"
        change_symbol = "+" if market["change_pct"] >= 0 else ""
        change_display = f"{change_symbol}{market['change_pct']:.2f}%"
    else:
        change_class = "neutral"
        change_display = "N/A"
    
    # Format technical data
    if tech_data["price"]:
        tech_signal_class = "positive" if tech_data["signal"] == "BUY" else ("negative" if tech_data["signal"] == "SELL" else "neutral")
        rsi_class = "alert" if tech_data["rsi_status"] == "Overbought" else ("positive" if tech_data["rsi_status"] == "Oversold" else "neutral")
    else:
        tech_signal_class = "neutral"
        rsi_class = "neutral"
    
    # Format news sentiment
    news_sentiment = fundamentals.get("news_sentiment", "NEUTRAL")
    if "DEFICIT" in news_sentiment or news_sentiment == "BULLISH":
        news_sentiment_class = "negative"  # Red = supply concern = bullish for prices
        news_sentiment_display = f"🔴 {news_sentiment}"
    elif "SURPLUS" in news_sentiment or news_sentiment == "BEARISH":
        news_sentiment_class = "positive"  # Green = supply comfort = bearish for prices
        news_sentiment_display = f"🟢 {news_sentiment}"
    else:
        news_sentiment_class = "neutral"
        news_sentiment_display = f"⚪ {news_sentiment}"
    
    # Build weather cards HTML
    weather_cards = ""
    for region, data in weather["regions"].items():
        drought_class = "alert" if data["drought_status"] != "Normal" else "ok"
        heat_class = "alert" if data["heat_status"] != "Normal" else "ok"
        harmattan_class = "alert" if data["harmattan_status"] != "Normal" else "ok"
        
        weather_cards += f"""
            <div class="region-card">
                <h4>📍 {region}</h4>
                <div class="metric">
                    <span class="label">Drought:</span>
                    <span class="{drought_class}">{data['drought_status_display']}</span>
                </div>
                <div class="metric">
                    <span class="label">Z-Score:</span>
                    <span>{data['z_score']:.2f}</span>
                </div>
                <div class="metric">
                    <span class="label">Heat:</span>
                    <span class="{heat_class}">{data['heat_status_display']}</span>
                </div>
                <div class="metric">
                    <span class="label">Days &gt;32°C:</span>
                    <span>{data['days_above_32']}</span>
                </div>
                <div class="metric">
                    <span class="label">Harmattan:</span>
                    <span class="{harmattan_class}">{data['harmattan_status_display']}</span>
                </div>
                <div class="metric">
                    <span class="label">Rainfall:</span>
                    <span>{data['current_rainfall']:.1f}mm</span>
                </div>
            </div>
        """
    
    # Build active signals HTML
    signals_html = ""
    if active_signals:
        for signal_type, signal_name in active_signals:
            icon = "🔴" if signal_type == "BEARISH" else "🟢"
            signals_html += f'<div class="signal">{icon} {signal_name}</div>'
    else:
        signals_html = '<div class="signal neutral">No active fundamental signals</div>'
    
    # Generate timestamp
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    
    # Build the HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cocoa Intelligence Unit</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Courier New', monospace;
            background: #0a0a0a;
            color: #00ff88;
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            padding: 40px 0;
            border-bottom: 2px solid #00ff88;
            margin-bottom: 30px;
        }}
        
        h1 {{
            font-size: 3em;
            text-shadow: 0 0 20px #00ff88;
            letter-spacing: 5px;
        }}
        
        .subtitle {{
            color: #888;
            margin-top: 10px;
            font-size: 0.9em;
        }}
        
        .timestamp {{
            color: #666;
            font-size: 0.8em;
            margin-top: 15px;
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: #111;
            border: 1px solid #333;
            border-radius: 10px;
            padding: 25px;
            transition: all 0.3s ease;
        }}
        
        .card:hover {{
            border-color: #00ff88;
            box-shadow: 0 0 20px rgba(0, 255, 136, 0.2);
        }}
        
        .card h3 {{
            font-size: 1.2em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #333;
        }}
        
        .metric {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #222;
        }}
        
        .metric:last-child {{
            border-bottom: none;
        }}
        
        .label {{
            color: #888;
        }}
        
        .price {{
            font-size: 2em;
            font-weight: bold;
            text-shadow: 0 0 10px #00ff88;
        }}
        
        .tech-signal {{
            font-size: 1.5em;
            font-weight: bold;
            text-align: center;
            padding: 10px;
            margin-bottom: 15px;
            border-radius: 5px;
        }}
        
        .positive {{
            color: #00ff88;
        }}
        
        .negative {{
            color: #ff4444;
        }}
        
        .alert {{
            color: #ff8800;
        }}
        
        .ok {{
            color: #00ff88;
        }}
        
        .neutral {{
            color: #888;
        }}
        
        .region-card {{
            background: #1a1a1a;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }}
        
        .region-card h4 {{
            margin-bottom: 10px;
            color: #00ff88;
        }}
        
        .verdict-banner {{
            background: linear-gradient(135deg, #111 0%, #1a1a1a 100%);
            border: 2px solid #00ff88;
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            margin-top: 30px;
        }}
        
        .verdict-extreme {{
            border-color: #ff0000;
            box-shadow: 0 0 30px rgba(255, 0, 0, 0.3);
        }}
        
        .verdict-extreme h2 {{
            color: #ff0000;
            text-shadow: 0 0 20px #ff0000;
        }}
        
        .verdict-high {{
            border-color: #ff8800;
            box-shadow: 0 0 30px rgba(255, 136, 0, 0.3);
        }}
        
        .verdict-high h2 {{
            color: #ff8800;
            text-shadow: 0 0 20px #ff8800;
        }}
        
        .verdict-moderate {{
            border-color: #00ff88;
            box-shadow: 0 0 30px rgba(0, 255, 136, 0.3);
        }}
        
        .verdict-neutral {{
            border-color: #666;
        }}
        
        .verdict-neutral h2 {{
            color: #888;
        }}
        
        .verdict-banner h2 {{
            font-size: 2.5em;
            margin-bottom: 15px;
        }}
        
        .verdict-banner .description {{
            font-size: 1.2em;
            color: #888;
            margin-bottom: 20px;
        }}
        
        .verdict-banner .multiplier {{
            font-size: 1.5em;
            color: #00ff88;
        }}
        
        .strategy-section {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin: 25px 0;
            text-align: left;
        }}
        
        .strategy-box {{
            background: #1a1a1a;
            padding: 20px;
            border-radius: 10px;
        }}
        
        .strategy-box h4 {{
            color: #00ff88;
            margin-bottom: 10px;
            font-size: 1.1em;
        }}
        
        .strategy-box p {{
            color: #ccc;
            line-height: 1.6;
        }}
        
        .narrative-section {{
            background: #1a1a1a;
            border-radius: 10px;
            padding: 25px;
            margin: 25px 0;
            text-align: left;
        }}
        
        .narrative-section h4 {{
            color: #00ff88;
            margin-bottom: 15px;
            font-size: 1.1em;
        }}
        
        .narrative-text {{
            color: #e0e0e0;
            font-size: 0.95em;
            line-height: 1.8;
        }}
        
        .narrative-text .driver {{
            color: #fff;
            margin-bottom: 10px;
        }}
        
        .narrative-text .chart {{
            color: #ccc;
            margin-bottom: 10px;
        }}
        
        .narrative-text .context {{
            color: #ff8800;
        }}
        
        .signals-container {{
            margin-top: 20px;
            display: flex;
            justify-content: center;
            gap: 15px;
            flex-wrap: wrap;
        }}
        
        .signal {{
            background: #222;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }}
        
        footer {{
            text-align: center;
            padding: 30px;
            color: #444;
            font-size: 0.8em;
        }}
        
        @media (max-width: 768px) {{
            .strategy-section {{
                grid-template-columns: 1fr;
            }}
            h1 {{
                font-size: 2em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🍫 COCOA INTELLIGENCE UNIT</h1>
            <div class="subtitle">Weather-Driven Commodity Trading System</div>
            <div class="timestamp">Last Updated: {timestamp}</div>
        </header>
        
        <div class="grid">
            <!-- Market Card -->
            <div class="card">
                <h3>📊 MARKET</h3>
                <div class="price">${market['price']:,.2f}</div>
                <div class="metric">
                    <span class="label">ICE Cocoa Futures (CC=F)</span>
                </div>
                <div class="metric">
                    <span class="label">Daily Change</span>
                    <span class="{change_class}">{change_display}</span>
                </div>
                <div class="metric">
                    <span class="label">Previous Close</span>
                    <span>${market['previous_close']:,.2f}</span>
                </div>
            </div>
            
            <!-- Technical Analysis Card -->
            <div class="card">
                <h3>📈 TECHNICALS</h3>
                <div class="tech-signal {tech_signal_class}">{tech_data['signal']}</div>
                <div class="metric">
                    <span class="label">SMA (50)</span>
                    <span>${tech_data['sma']:,.2f}</span>
                </div>
                <div class="metric">
                    <span class="label">RSI (14)</span>
                    <span class="{rsi_class}">{tech_data['rsi']:.1f}</span>
                </div>
                <div class="metric">
                    <span class="label">Trend</span>
                    <span>{tech_data['trend_display']}</span>
                </div>
                <div class="metric">
                    <span class="label">RSI Status</span>
                    <span class="{rsi_class}">{tech_data['rsi_display']}</span>
                </div>
            </div>
            
            <!-- Fundamentals Card -->
            <div class="card">
                <h3>📦 FUNDAMENTALS</h3>
                <div class="metric">
                    <span class="label">Stocks-to-Usage</span>
                    <span class="{'alert' if fundamentals['stocks_ratio'] < 30 else 'ok'}">{fundamentals['stocks_ratio']}%</span>
                </div>
                <div class="metric">
                    <span class="label">Status</span>
                    <span>{fundamentals['status_display']}</span>
                </div>
                <div class="metric">
                    <span class="label">News Sentiment</span>
                    <span class="{news_sentiment_class}">{news_sentiment_display}</span>
                </div>
                <div class="metric">
                    <span class="label">Position Multiplier</span>
                    <span class="positive">{fundamentals['multiplier']}x</span>
                </div>
            </div>
            
            <!-- ENSO Card -->
            <div class="card">
                <h3>🌍 CLIMATE (ENSO)</h3>
                <div class="metric">
                    <span class="label">ONI Value</span>
                    <span>{enso['value']:.2f}</span>
                </div>
                <div class="metric">
                    <span class="label">Period</span>
                    <span>{enso['month']} {enso['year']}</span>
                </div>
                <div class="metric">
                    <span class="label">Signal</span>
                    <span>{enso['display']}</span>
                </div>
            </div>
            
            <!-- Weather Card -->
            <div class="card">
                <h3>🌦️ WEATHER (AFRICA)</h3>
                {weather_cards}
                {'<div class="alert" style="text-align:center;padding:10px;margin-top:10px;">🚨 DUAL-REGION DROUGHT 🚨</div>' if weather['dual_region_drought_detected'] else ''}
            </div>
        </div>
        
        <!-- Verdict Banner -->
        <div class="verdict-banner {verdict_class}">
            <h2>{verdict}</h2>
            <div class="description">{description}</div>
            
            <div class="narrative-section">
                <h4>📝 MARKET ANALYSIS</h4>
                <div class="narrative-text">
                    <p class="driver">🎯 <strong>The Driver:</strong> {narrative['driver']}</p>
                    <p class="chart">📊 <strong>The Chart:</strong> {narrative['chart']}</p>
                    <p class="context">🌦️ <strong>The Context:</strong> {narrative['context']}</p>
                </div>
            </div>
            
            <div class="strategy-section">
                <div class="strategy-box">
                    <h4>🎯 STRATEGY (Fundamental)</h4>
                    <p>Risk Appetite: {verdict}<br>
                    Position Size: {multiplier}x Standard Lots</p>
                </div>
                <div class="strategy-box">
                    <h4>⚡ TACTICS (Technical)</h4>
                    <p>Signal: {tech_data['signal']}<br>
                    Trend: {tech_data['trend']} | RSI: {tech_data['rsi']:.0f}</p>
                </div>
            </div>
            
            <div class="multiplier">Recommended Position Size: {multiplier}x Standard Lots</div>
            <div class="signals-container">
                {signals_html}
            </div>
        </div>
        
        <footer>
            Cocoa Intelligence Unit | Data Sources: Open-Meteo, NOAA, Yahoo Finance<br>
            For educational purposes only. Not financial advice.
        </footer>
    </div>
</body>
</html>
"""
    
    # Write the HTML file
    with open("index.html", "w") as f:
        f.write(html)
    
    return "index.html"


if __name__ == "__main__":
    output_file = generate_html()
    print(f"Dashboard generated: {output_file}")
