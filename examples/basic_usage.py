#!/usr/bin/env python3
"""
Basic usage example for WSJ Adapter.

This example demonstrates the basic functionality of the WSJ Adapter
for downloading articles from the Wall Street Journal via the Wayback Machine.
"""

import datetime
from wsj_adapter import WSJAdapter

def main():
    """
    Basic example of using WSJ Adapter to download articles.
    """
    print("WSJ Adapter - Basic Usage Example")
    print("=" * 40)
    
    # Initialize the adapter with a small date range for testing
    adapter = WSJAdapter(
        start_date=datetime.date(2024, 1, 1),
        end_date=datetime.date(2024, 1, 2),
        topics=['/business/', '/finance/'],  # Focus on business and finance
        max_workers=2,  # Use fewer workers for testing
        latest_records=True,  # Get only latest record per day
        latest_articles=True  # Get only latest article per day
    )
    
    print(f"Configured adapter for date range: {adapter.start_date} to {adapter.end_date}")
    print(f"Topics: {adapter.topics}")
    print(f"Max workers: {adapter.max_workers}")
    print()
    
    # Download articles
    print("Starting download...")
    try:
        articles = adapter.download()
        
        print(f"Successfully downloaded {len(articles)} articles")
        print()
        
        # Display first few articles
        for i, article in enumerate(articles[:3]):
            print(f"Article {i + 1}:")
            print(f"  Headline: {article.get('headline', 'N/A')}")
            print(f"  Date: {article.get('date', 'N/A')}")
            print(f"  Summary: {article.get('summary', 'N/A')[:100]}...")
            print(f"  Companies: {article.get('companies', 'N/A')}")
            print(f"  URL: {article.get('url', 'N/A')}")
            print()
            
        if len(articles) > 3:
            print(f"... and {len(articles) - 3} more articles")
            
    except Exception as e:
        print(f"Error during download: {e}")
        return
    
    print("Basic usage example completed!")

if __name__ == "__main__":
    main() 