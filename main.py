#!/usr/bin/env python3
"""
Cocoa Trading Desk - Main Dashboard
Integrates weather, climate, market, and fundamental analysis for cocoa trading decisions.
"""

from fetch_history import analyze_weather
from fetch_enso import get_enso_signal
from fetch_market import get_market_data
from check_fundamentals import get_fundamental_multiplier, get_fundamentals_analysis


def print_header():
    """Print the dashboard header."""
    header = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     ██████╗ ██████╗  ██████╗ ██████╗  █████╗    ████████╗██████╗  █████╗     ║
║    ██╔════╝██╔═══██╗██╔════╝██╔═══██╗██╔══██╗   ╚══██╔══╝██╔══██╗██╔══██╗    ║
║    ██║     ██║   ██║██║     ██║   ██║███████║      ██║   ██████╔╝███████║    ║
║    ██║     ██║   ██║██║     ██║   ██║██╔══██║      ██║   ██╔══██╗██╔══██║    ║
║    ╚██████╗╚██████╔╝╚██████╗╚██████╔╝██║  ██║      ██║   ██║  ██║██║  ██║    ║
║     ╚═════╝ ╚═════╝  ╚═════╝ ╚═════╝ ╚═╝  ╚═╝      ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝    ║
║                                                                              ║
║                    🍫 COCOA TRADING DESK 🍫                                  ║
║                   Weather-Driven Trading System                              ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(header)


def print_section(title):
    """Print a section divider."""
    print(f"\n{'─' * 78}")
    print(f"  {title}")
    print(f"{'─' * 78}")


def calculate_risk_appetite(weather, enso, fundamentals_analysis):
    """
    Calculate final risk appetite based on all signals.
    
    Returns:
        tuple: (appetite_level, description, multiplier)
    """
    signals = []
    
    # Check for dual-region drought (strongest bullish signal)
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
    
    # Check ENSO signal
    if enso["signal"] == "BULLISH":
        signals.append(("BULLISH", "El Niño Active"))
    elif enso["signal"] == "BEARISH":
        signals.append(("BEARISH", "La Niña Active"))
    
    # Get fundamental multiplier
    multiplier = fundamentals_analysis["multiplier"]
    
    # Determine overall appetite
    bullish_count = sum(1 for s in signals if s[0] in ["BULLISH", "EXTREME_BULLISH"])
    extreme_count = sum(1 for s in signals if s[0] == "EXTREME_BULLISH")
    bearish_count = sum(1 for s in signals if s[0] == "BEARISH")
    
    if extreme_count > 0:
        appetite = "🚨 MAXIMUM CONVICTION"
        description = "Dual-region supply shock - highest probability trade"
    elif bullish_count >= 2:
        appetite = "🔥 HIGH CONVICTION"
        description = "Multiple bullish signals aligned"
    elif bullish_count == 1:
        appetite = "📈 MODERATE BULLISH"
        description = "Single bullish signal active"
    elif bearish_count > 0:
        appetite = "⚠️ CAUTIOUS"
        description = "Bearish climate signal present"
    else:
        appetite = "⚪ NEUTRAL"
        description = "No strong directional signals"
    
    return appetite, description, multiplier, signals


def run_dashboard():
    """Run the main trading dashboard."""
    print_header()
    
    # Collect all data
    print("\n  ⏳ Fetching data from all sources...")
    
    weather = analyze_weather()
    enso = get_enso_signal()
    market = get_market_data()
    fundamentals = get_fundamentals_analysis()
    
    # === MARKET SECTION ===
    print_section("📊 MARKET DATA")
    if market["price"]:
        change_symbol = "+" if market["change_pct"] >= 0 else ""
        change_color = "🟢" if market["change_pct"] >= 0 else "🔴"
        print(f"  ICE Cocoa Futures (CC=F)")
        print(f"  Current Price:  ${market['price']:,.2f}")
        print(f"  Daily Change:   {change_color} {change_symbol}{market['change_pct']:.2f}%")
    
    # === FUNDAMENTALS SECTION ===
    print_section("📦 MARKET FUNDAMENTALS")
    print(f"  Stocks-to-Usage Ratio: {fundamentals['stocks_ratio']}%")
    print(f"  Status: {fundamentals['status_display']}")
    print(f"  Position Multiplier:   {fundamentals['multiplier']}x")
    
    # === ENSO SECTION ===
    print_section("🌍 GLOBAL CLIMATE (ENSO)")
    print(f"  ONI Value: {enso['value']:.2f} ({enso['month']} {enso['year']})")
    print(f"  Signal:    {enso['display']}")
    
    # === WEATHER SECTION ===
    print_section("🌦️ REGIONAL WEATHER ANALYSIS")
    for region, data in weather["regions"].items():
        print(f"\n  📍 {region}")
        print(f"     Drought:   {data['drought_status_display']} (Z-Score: {data['z_score']:.2f})")
        print(f"     Heat:      {data['heat_status_display']} ({data['days_above_32']} days > 32°C)")
        print(f"     Harmattan: {data['harmattan_status_display']}")
        print(f"     Rainfall:  {data['current_rainfall']:.1f}mm (Avg: {data['average_rainfall']:.1f}mm)")
    
    # Dual-region check
    if weather["dual_region_drought_detected"]:
        print(f"\n  🚨🚨🚨 DUAL-REGION DROUGHT DETECTED! 🚨🚨🚨")
    
    # === TRADING SIGNAL SECTION ===
    print_section("🎯 TRADING SIGNAL SUMMARY")
    
    appetite, description, multiplier, active_signals = calculate_risk_appetite(
        weather, enso, fundamentals
    )
    
    print(f"\n  Risk Appetite:     {appetite}")
    print(f"  Rationale:         {description}")
    print(f"  Position Sizing:   {multiplier}x standard lots")
    
    if active_signals:
        print(f"\n  Active Signals:")
        for signal_type, signal_name in active_signals:
            icon = "🔴" if signal_type == "BEARISH" else "🟢"
            print(f"    {icon} {signal_name}")
    else:
        print(f"\n  Active Signals:    None")
    
    # Final recommendation
    print_section("💡 RECOMMENDATION")
    
    if appetite in ["🚨 MAXIMUM CONVICTION", "🔥 HIGH CONVICTION"]:
        print(f"  ➤ LONG BIAS with {multiplier}x position size")
        print(f"  ➤ Weather conditions favor supply disruption")
    elif appetite == "📈 MODERATE BULLISH":
        print(f"  ➤ CAUTIOUS LONG with {multiplier}x position size")
        print(f"  ➤ Monitor for additional confirmation signals")
    elif appetite == "⚠️ CAUTIOUS":
        print(f"  ➤ REDUCE EXPOSURE or stay flat")
        print(f"  ➤ Bearish climate factors present")
    else:
        print(f"  ➤ NO STRONG DIRECTIONAL BIAS")
        print(f"  ➤ Wait for clearer signals before entering")
    
    print(f"\n{'═' * 78}\n")
    
    return {
        "weather": weather,
        "enso": enso,
        "market": market,
        "fundamentals": fundamentals,
        "appetite": appetite,
        "multiplier": multiplier
    }


if __name__ == "__main__":
    run_dashboard()
