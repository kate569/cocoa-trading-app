#!/usr/bin/env python3
"""
Fetch and analyze news sentiment for cocoa market.
Scans Google News RSS for bullish/bearish keywords.
"""

import json
import feedparser


# Keywords that indicate bullish sentiment (supply concerns = higher prices)
BULLISH_KEYWORDS = [
    "shortage", "deficit", "drought", "soaring", "record high", "crisis",
    "supply crunch", "surge", "rally", "spike", "scarce", "tight supply",
    "production fall", "crop damage", "disease", "pest", "el nino",
    "weather concern", "supply risk", "all-time high"
]

# Keywords that indicate bearish sentiment (supply comfort = lower prices)
BEARISH_KEYWORDS = [
    "surplus", "oversupply", "record harvest", "drop", "falling", "rain",
    "recovery", "bumper crop", "abundant", "plunge", "decline", "slump",
    "production rise", "good weather", "favorable", "output increase",
    "stockpile", "glut", "excess"
]


def fetch_news_feed():
    """Fetch Google News RSS feed for cocoa market."""
    url = "https://news.google.com/rss/search?q=cocoa+commodity+market&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    return feed.entries[:10]  # Get last 10 articles


def analyze_headline(title):
    """
    Analyze a headline for bullish/bearish keywords.
    
    Returns:
        tuple: (bullish_matches, bearish_matches)
    """
    title_lower = title.lower()
    
    bullish_matches = [kw for kw in BULLISH_KEYWORDS if kw in title_lower]
    bearish_matches = [kw for kw in BEARISH_KEYWORDS if kw in title_lower]
    
    return bullish_matches, bearish_matches


def get_news_sentiment():
    """
    Analyze news sentiment and return results.
    
    Returns:
        dict: {
            "bullish_count": int,
            "bearish_count": int,
            "sentiment": str,
            "headlines_analyzed": list,
            "bullish_headlines": list,
            "bearish_headlines": list
        }
    """
    entries = fetch_news_feed()
    
    total_bullish = 0
    total_bearish = 0
    headlines_analyzed = []
    bullish_headlines = []
    bearish_headlines = []
    
    for entry in entries:
        title = entry.get("title", "")
        bullish_matches, bearish_matches = analyze_headline(title)
        
        headlines_analyzed.append({
            "title": title,
            "bullish_keywords": bullish_matches,
            "bearish_keywords": bearish_matches
        })
        
        if bullish_matches:
            total_bullish += len(bullish_matches)
            bullish_headlines.append((title, bullish_matches))
        
        if bearish_matches:
            total_bearish += len(bearish_matches)
            bearish_headlines.append((title, bearish_matches))
    
    # Determine sentiment
    if total_bullish > total_bearish:
        sentiment = "BULLISH"
        status = "CRITICAL DEFICIT"
    elif total_bearish > total_bullish:
        sentiment = "BEARISH"
        status = "SURPLUS"
    else:
        sentiment = "NEUTRAL"
        status = "NEUTRAL"
    
    return {
        "bullish_count": total_bullish,
        "bearish_count": total_bearish,
        "sentiment": sentiment,
        "status": status,
        "headlines_analyzed": headlines_analyzed,
        "bullish_headlines": bullish_headlines,
        "bearish_headlines": bearish_headlines
    }


def update_fundamentals(status):
    """Update fundamentals.json with news sentiment status."""
    filepath = "fundamentals.json"
    
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    
    data["news_sentiment_status"] = status
    
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    
    return data


def main():
    """Run news sentiment analysis and update fundamentals."""
    print("📰 Cocoa News Sentiment Analysis")
    print("=" * 60)
    print("\nFetching news from Google News RSS...\n")
    
    result = get_news_sentiment()
    
    print(f"Headlines Analyzed: {len(result['headlines_analyzed'])}")
    print(f"Bullish Keywords Found: {result['bullish_count']}")
    print(f"Bearish Keywords Found: {result['bearish_count']}")
    print(f"\nSentiment: {result['sentiment']}")
    print(f"Status: {result['status']}")
    
    # Show triggering headlines
    if result["bullish_headlines"]:
        print("\n🟢 BULLISH Headlines:")
        for title, keywords in result["bullish_headlines"]:
            print(f"  • {title[:80]}...")
            print(f"    Keywords: {', '.join(keywords)}")
    
    if result["bearish_headlines"]:
        print("\n🔴 BEARISH Headlines:")
        for title, keywords in result["bearish_headlines"]:
            print(f"  • {title[:80]}...")
            print(f"    Keywords: {', '.join(keywords)}")
    
    if not result["bullish_headlines"] and not result["bearish_headlines"]:
        print("\n⚪ No strong sentiment keywords detected in recent headlines.")
    
    # Update fundamentals.json
    print("\n" + "-" * 60)
    updated_data = update_fundamentals(result["status"])
    print(f"Updated fundamentals.json with news_sentiment_status: {result['status']}")
    
    return result


if __name__ == "__main__":
    main()
