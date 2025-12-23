#!/usr/bin/env python3
"""
Generate detailed market narrative based on all trading signals.
Includes holding time estimates and correlated risk analysis.
"""


def analyze_weather_triggers(weather_data):
    """
    Analyze weather data to identify specific triggers and their implications.
    
    Returns:
        dict with trigger types, affected regions, and severity
    """
    triggers = {
        "drought_regions": [],
        "heat_regions": [],
        "harmattan_regions": [],
        "dual_region_stress": False,
        "stressed_regions": []
    }
    
    for region, data in weather_data["regions"].items():
        is_stressed = False
        
        if data["drought_status"] == "Severe Drought":
            triggers["drought_regions"].append(region)
            is_stressed = True
        
        if data["heat_status"] == "Critical Heat":
            triggers["heat_regions"].append(region)
            is_stressed = True
        
        if data["harmattan_status"] == "Harmattan Active":
            triggers["harmattan_regions"].append(region)
            is_stressed = True
        
        if is_stressed:
            triggers["stressed_regions"].append(region)
    
    # Check for dual-region stress (correlated risk)
    if len(triggers["stressed_regions"]) >= 2:
        triggers["dual_region_stress"] = True
    
    return triggers


def calculate_holding_time(triggers, enso_signal=None):
    """
    Calculate estimated holding time based on the type of weather trigger.
    
    Logic from strategy:
    - Drought: Exit in 3-4 weeks once rains return or SPI > -1.0
    - El Niño: Hold for 6-8 months to capture full supply disruption
    - Heat Stress: Exit in 8-10 months as this affects future main crop
    """
    holding_times = []
    exit_conditions = []
    
    # Drought-based holding
    if triggers["drought_regions"]:
        holding_times.append({
            "trigger": "Drought",
            "duration": "3-4 weeks",
            "exit_condition": "Exit when rains return or Z-Score (SPI) rises above -1.0",
            "rationale": "Drought premium decays quickly once precipitation normalizes"
        })
    
    # Heat stress-based holding
    if triggers["heat_regions"]:
        holding_times.append({
            "trigger": "Heat Stress",
            "duration": "8-10 months",
            "exit_condition": "Exit before main crop harvest in October-December",
            "rationale": "Heat damage affects pod development for the NEXT main crop season"
        })
    
    # Harmattan-based holding
    if triggers["harmattan_regions"]:
        holding_times.append({
            "trigger": "Harmattan Winds",
            "duration": "4-6 weeks",
            "exit_condition": "Exit when humidity rises above 50% and winds calm",
            "rationale": "Harmattan drying risk is seasonal and temporary"
        })
    
    # El Niño override (longest hold)
    if enso_signal == "BULLISH":
        holding_times.append({
            "trigger": "El Niño",
            "duration": "6-8 months",
            "exit_condition": "Exit when ONI drops below +0.5 or full crop cycle completes",
            "rationale": "El Niño creates persistent drought conditions with 6-8 month lag to production impact"
        })
    
    # If no specific triggers, return neutral
    if not holding_times:
        return {
            "primary_duration": "N/A - No active position recommended",
            "all_triggers": [],
            "exit_summary": "Wait for clear weather or fundamental trigger before entering"
        }
    
    # Find the longest duration (most significant trigger)
    duration_order = ["6-8 months", "8-10 months", "4-6 weeks", "3-4 weeks"]
    primary = holding_times[0]
    for ht in holding_times:
        if duration_order.index(ht["duration"]) < duration_order.index(primary["duration"]):
            primary = ht
    
    return {
        "primary_duration": primary["duration"],
        "primary_trigger": primary["trigger"],
        "primary_exit": primary["exit_condition"],
        "primary_rationale": primary["rationale"],
        "all_triggers": holding_times,
        "exit_summary": primary["exit_condition"]
    }


def generate_correlated_risk_warning(triggers, stocks_ratio):
    """
    Generate warning about correlated supply destruction.
    
    When BOTH regions are under stress, the market typically underestimates
    the 18-25% supply destruction potential.
    """
    if not triggers["dual_region_stress"]:
        return None
    
    regions_affected = ", ".join(triggers["stressed_regions"])
    
    warning = f"""🚨 CORRELATED SUPPLY DESTRUCTION WARNING 🚨

Both {regions_affected} are experiencing simultaneous weather stress. This is a rare and critical situation.

Historical Analysis:
• When both Côte d'Ivoire AND Ghana face concurrent stress, supply losses reach 18-25%
• Markets typically underestimate correlated risk by 30-40%
• Current stocks-to-usage at {stocks_ratio}% provides ZERO buffer for such losses

Implication: This is a HIGH CONVICTION scenario. The market has not yet priced in the full extent of potential supply destruction. Price targets should be revised significantly upward."""
    
    return warning


def generate_amplifier_explanation(stocks_ratio, multiplier):
    """
    Explain why low stocks amplify weather signals.
    """
    if stocks_ratio >= 35:
        return """💡 WHY THIS SIGNAL?

Current stocks-to-usage ratio is healthy at {stocks_ratio}%. This means the market has adequate buffer inventory to absorb minor weather disruptions. Weather signals carry NORMAL weight in this environment.""".format(stocks_ratio=stocks_ratio)
    
    elif stocks_ratio >= 30:
        return """💡 WHY THIS SIGNAL?

Stocks-to-usage ratio at {stocks_ratio}% is below comfortable levels. The market has LIMITED buffer:

• Normal buffer zone: 35-45%
• Current level: {stocks_ratio}% (LOW)
• Amplification factor: 2.0x

Any weather disruption now has DOUBLE the price impact because there's no inventory cushion to smooth out supply shocks. The {multiplier}x position multiplier reflects this vulnerability.""".format(stocks_ratio=stocks_ratio, multiplier=multiplier)
    
    else:
        return """💡 WHY THIS SIGNAL?

CRITICAL: Stocks-to-usage ratio at {stocks_ratio}% represents a structural deficit:

• Normal buffer zone: 35-45%
• Current level: {stocks_ratio}% (CRITICAL DEFICIT)
• Amplification factor: 2.5x

This is the LOWEST stocks level in recent history. The cocoa market is operating with virtually NO safety margin:

1. ANY weather shock gets amplified 2.5x in price impact
2. Buyers cannot source alternative supply - there is none
3. Processor margins are already squeezed to breaking point
4. The market is ONE bad harvest away from genuine crisis

The {multiplier}x position multiplier reflects maximum conviction. Even minor weather concerns in this environment can trigger outsized price moves.""".format(stocks_ratio=stocks_ratio, multiplier=multiplier)


def generate_market_narrative(technical_data, fundamental_data, weather_data, news_sentiment, enso_data=None):
    """
    Generate a comprehensive market narrative with detailed analysis.
    
    Args:
        technical_data: Dict from get_technical_analysis()
        fundamental_data: Dict from get_fundamentals_analysis()
        weather_data: Dict from analyze_weather()
        news_sentiment: String news sentiment status
        enso_data: Optional dict from get_enso_signal()
    
    Returns:
        dict with full narrative, holding times, and risk warnings
    """
    stocks_ratio = fundamental_data["stocks_ratio"]
    multiplier = fundamental_data["multiplier"]
    
    # Analyze weather triggers
    triggers = analyze_weather_triggers(weather_data)
    
    # Get ENSO signal if provided
    enso_signal = enso_data.get("signal") if enso_data else None
    
    # Calculate holding time
    holding_info = calculate_holding_time(triggers, enso_signal)
    
    # Generate correlated risk warning
    correlated_warning = generate_correlated_risk_warning(triggers, stocks_ratio)
    
    # Generate amplifier explanation
    amplifier_explanation = generate_amplifier_explanation(stocks_ratio, multiplier)
    
    # === PARAGRAPH 1: FUNDAMENTAL BACKDROP ===
    if stocks_ratio < 30:
        fundamental_para = f"""The cocoa market is in a state of structural deficit with global stocks-to-usage at just {stocks_ratio}%. This represents one of the tightest supply situations in recent history, leaving the market exceptionally vulnerable to any supply disruption. With {news_sentiment.lower()} news flow currently, the fundamental backdrop remains firmly supportive for prices."""
    elif stocks_ratio < 35:
        fundamental_para = f"""Global cocoa inventories remain below comfortable levels at {stocks_ratio}% stocks-to-usage ratio. While not yet critical, this limited buffer means the market has reduced capacity to absorb supply shocks. Current news sentiment is {news_sentiment.lower()}, adding to the cautious tone."""
    else:
        fundamental_para = f"""The fundamental picture shows adequate inventory levels with {stocks_ratio}% stocks-to-usage. The market has reasonable buffer capacity to handle minor disruptions. News sentiment is currently {news_sentiment.lower()}."""
    
    # === PARAGRAPH 2: TECHNICAL POSITIONING ===
    if technical_data["price"] is None:
        technical_para = "Technical analysis is currently unavailable due to data limitations."
    else:
        trend = technical_data["trend"]
        rsi = technical_data["rsi"]
        sma = technical_data.get("sma", 0)
        price = technical_data["price"]
        
        if trend == "Uptrend":
            trend_text = f"Price at ${price:,.0f} trades above the 50-day SMA (${sma:,.0f}), confirming the bullish trend structure"
        else:
            trend_text = f"Price at ${price:,.0f} has fallen below the 50-day SMA (${sma:,.0f}), suggesting trend weakness"
        
        if rsi > 70:
            rsi_text = f"RSI at {rsi:.0f} indicates overbought conditions - consider waiting for a pullback before adding exposure"
        elif rsi < 30:
            rsi_text = f"RSI at {rsi:.0f} shows deeply oversold conditions - this may present a tactical buying opportunity"
        elif rsi > 60:
            rsi_text = f"RSI at {rsi:.0f} shows healthy bullish momentum with room to run before reaching overbought territory"
        elif rsi < 40:
            rsi_text = f"RSI at {rsi:.0f} indicates weakening momentum - caution advised on new long positions"
        else:
            rsi_text = f"RSI at {rsi:.0f} sits in neutral territory, suggesting balanced buying and selling pressure"
        
        technical_para = f"{trend_text}. {rsi_text}."
    
    # === PARAGRAPH 3: WEATHER & RISK CONTEXT ===
    weather_alerts = []
    for region, data in weather_data["regions"].items():
        region_alerts = []
        if data["drought_status"] == "Severe Drought":
            region_alerts.append("severe drought")
        if data["heat_status"] == "Critical Heat":
            region_alerts.append("critical heat stress")
        if data["harmattan_status"] == "Harmattan Active":
            region_alerts.append("active Harmattan winds")
        
        if region_alerts:
            weather_alerts.append(f"{region} ({', '.join(region_alerts)})")
    
    if weather_data["dual_region_drought_detected"]:
        weather_para = f"""⚠️ CRITICAL WEATHER ALERT: Both major producing regions are experiencing severe drought conditions simultaneously. This correlated stress pattern historically results in 18-25% supply destruction. The market is likely UNDERPRICING this risk. Affected regions: {', '.join(weather_alerts)}."""
    elif weather_alerts:
        weather_para = f"""Weather monitoring has identified stress conditions in: {', '.join(weather_alerts)}. These conditions may impact near-term supply and should be monitored closely for deterioration or improvement."""
    else:
        weather_para = "Current weather conditions across West African cocoa regions are within normal seasonal parameters. No immediate supply threats detected from meteorological factors."
    
    # Combine full narrative
    full_narrative = f"{fundamental_para}\n\n{technical_para}\n\n{weather_para}"
    
    # Add correlated warning if applicable
    if correlated_warning:
        full_narrative += f"\n\n{correlated_warning}"
    
    return {
        "fundamental_paragraph": fundamental_para,
        "technical_paragraph": technical_para,
        "weather_paragraph": weather_para,
        "full_narrative": full_narrative,
        "holding_time": holding_info,
        "correlated_warning": correlated_warning,
        "amplifier_explanation": amplifier_explanation,
        "triggers": triggers,
        # Legacy fields for compatibility
        "driver": fundamental_para,
        "chart": technical_para,
        "context": weather_para
    }


def main():
    """Test the narrative generator with sample data."""
    tech_data = {
        "price": 5800,
        "sma": 5750,
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
    
    enso_data = {"signal": "NEUTRAL", "value": -0.45}
    
    narrative = generate_market_narrative(
        tech_data, fundamental_data, weather_data, "NEUTRAL", enso_data
    )
    
    print("📝 Market Narrative Generator Test")
    print("=" * 70)
    print("\n📄 FULL NARRATIVE:")
    print(narrative['full_narrative'])
    print("\n" + "=" * 70)
    print("\n🕒 HOLDING TIME:")
    print(f"Duration: {narrative['holding_time']['primary_duration']}")
    if narrative['holding_time'].get('primary_exit'):
        print(f"Exit Condition: {narrative['holding_time']['primary_exit']}")
    print("\n" + "=" * 70)
    print(narrative['amplifier_explanation'])


if __name__ == "__main__":
    main()
