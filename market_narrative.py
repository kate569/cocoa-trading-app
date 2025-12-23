#!/usr/bin/env python3
"""
Generate human-readable market narrative based on all trading signals.
Creates a 3-sentence explanation of current market conditions.
"""


def generate_market_narrative(technical_data, fundamental_data, weather_data, news_sentiment):
    """
    Generate a 3-sentence market narrative.
    
    Args:
        technical_data: Dict from get_technical_analysis()
        fundamental_data: Dict from get_fundamentals_analysis()
        weather_data: Dict from analyze_weather()
        news_sentiment: String news sentiment status
    
    Returns:
        dict: {
            "driver": str,      # Sentence 1: Fundamental/News bias
            "chart": str,       # Sentence 2: Technical stance
            "context": str,     # Sentence 3: Weather risks
            "full_narrative": str  # All sentences combined
        }
    """
    
    # === SENTENCE 1: THE DRIVER (Fundamentals + News) ===
    stocks_ratio = fundamental_data["stocks_ratio"]
    multiplier = fundamental_data["multiplier"]
    
    # Determine fundamental stance
    if stocks_ratio < 30:
        fundamental_stance = "a critical supply deficit"
        fundamental_bias = "strongly bullish"
    elif stocks_ratio < 35:
        fundamental_stance = "low inventory levels"
        fundamental_bias = "moderately bullish"
    else:
        fundamental_stance = "healthy stock levels"
        fundamental_bias = "neutral"
    
    # Determine news stance
    if "DEFICIT" in news_sentiment or news_sentiment == "BULLISH":
        news_stance = "bullish news headlines"
    elif "SURPLUS" in news_sentiment or news_sentiment == "BEARISH":
        news_stance = "bearish news flow"
    else:
        news_stance = "mixed news sentiment"
    
    driver = f"Market fundamentals indicate {fundamental_stance} with {news_stance}, suggesting a {fundamental_bias} supply-side outlook."
    
    # === SENTENCE 2: THE CHART (Technical Analysis) ===
    if technical_data["price"] is None:
        chart = "Technical data is currently unavailable for analysis."
    else:
        trend = technical_data["trend"]
        rsi = technical_data["rsi"]
        rsi_status = technical_data["rsi_status"]
        signal = technical_data["signal"]
        
        # Describe trend
        if trend == "Uptrend":
            trend_desc = "the uptrend remains intact as price trades above the 50-day SMA"
        else:
            trend_desc = "price has weakened below the 50-day SMA, indicating a potential downtrend"
        
        # Describe momentum
        if rsi_status == "Overbought":
            momentum_desc = f"however, RSI at {rsi:.0f} signals overbought conditions and potential exhaustion"
        elif rsi_status == "Oversold":
            momentum_desc = f"with RSI at {rsi:.0f} indicating oversold conditions and potential buying opportunity"
        else:
            momentum_desc = f"with RSI at {rsi:.0f} showing balanced momentum"
        
        chart = f"Technically, {trend_desc}, {momentum_desc}."
    
    # === SENTENCE 3: THE CONTEXT (Weather Risks) ===
    alerts = []
    
    # Check for dual-region drought
    if weather_data["dual_region_drought_detected"]:
        alerts.append("CRITICAL: Both major producing regions are experiencing severe drought")
    
    # Check individual alerts
    for region, data in weather_data["regions"].items():
        if data["drought_status"] == "Severe Drought":
            alerts.append(f"Severe Drought in {region}")
        if data["heat_status"] == "Critical Heat":
            alerts.append(f"Heat Stress Alert in {region}")
        if data["harmattan_status"] == "Harmattan Active":
            alerts.append(f"Harmattan Winds affecting {region}")
    
    if alerts:
        if len(alerts) == 1:
            context = f"⚠️ Key Risk: {alerts[0]} may significantly impact near-term supply."
        else:
            alert_list = ", ".join(alerts[:-1]) + f" and {alerts[-1]}"
            context = f"⚠️ Multiple Risks: {alert_list} require close monitoring for supply disruption."
    else:
        context = "Weather conditions across West African cocoa regions are currently within normal parameters."
    
    # Combine all sentences
    full_narrative = f"{driver} {chart} {context}"
    
    return {
        "driver": driver,
        "chart": chart,
        "context": context,
        "full_narrative": full_narrative
    }


def main():
    """Test the narrative generator with sample data."""
    # Sample data for testing
    tech_data = {
        "price": 5800,
        "trend": "Uptrend",
        "rsi": 62,
        "rsi_status": "Neutral",
        "signal": "BUY"
    }
    
    fundamental_data = {
        "stocks_ratio": 29.5,
        "multiplier": 2.5,
        "status": "CRITICAL_DEFICIT",
        "status_display": "⚠️ CRITICAL DEFICIT"
    }
    
    weather_data = {
        "dual_region_drought_detected": False,
        "regions": {
            "San Pedro": {
                "drought_status": "Normal",
                "heat_status": "Normal",
                "harmattan_status": "Normal"
            },
            "Kumasi": {
                "drought_status": "Normal",
                "heat_status": "Critical Heat",
                "harmattan_status": "Normal"
            }
        }
    }
    
    news_sentiment = "NEUTRAL"
    
    narrative = generate_market_narrative(tech_data, fundamental_data, weather_data, news_sentiment)
    
    print("📝 Market Narrative Generator Test")
    print("=" * 60)
    print(f"\n🎯 THE DRIVER:\n{narrative['driver']}")
    print(f"\n📊 THE CHART:\n{narrative['chart']}")
    print(f"\n🌦️ THE CONTEXT:\n{narrative['context']}")
    print(f"\n📄 FULL NARRATIVE:\n{narrative['full_narrative']}")


if __name__ == "__main__":
    main()
