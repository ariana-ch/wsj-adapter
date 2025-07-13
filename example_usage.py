#!/usr/bin/env python3
"""
Example usage of the WSJ Adapter with the new functionality.
This script demonstrates:
1. Sampling a number of website captures for a given day
2. Processing multiple article links sequentially until one returns a result
"""

import datetime
import json
from src.wsj_adapter.wsj_adapter import WSJAdapter

def main():
    """Demonstrate the WSJ Adapter functionality."""
    
    # Create adapter with new parameters
    adapter = WSJAdapter(
        start_date=datetime.date(2022, 12, 10),
        end_date=datetime.date(2022, 12, 12),
        topics=['/business/', '/finance/'],  # Focus on business and finance
        max_workers=3,                       # Number of parallel workers
        no_of_captures=5                     # Sample 5 captures per day per topic
    )
    
    print("Starting WSJ article extraction...")
    print(f"Date range: {adapter.start_date} to {adapter.end_date}")
    print(f"Topics: {adapter.topics}")
    print(f"Max workers: {adapter.max_workers}")
    print(f"Captures per day: {adapter.no_of_captures}")
    print("-" * 50)
    
    # Download articles
    articles = adapter.download()
    
    # Print summary
    print(f"\n--- Download Summary ---")
    print(f"Total articles extracted: {len(articles)}")
    
    if articles:
        # Print first few articles as examples
        for i, article in enumerate(articles[:3]):
            print(f"\n--- Article {i + 1} ---")
            print(f"Headline: {article.get('headline', 'N/A')}")
            print(f"Date: {article.get('date', 'N/A')}")
            print(f"URL: {article.get('url', 'N/A')}")
            print(f"Summary: {article.get('summary', 'N/A')[:150]}...")
            print(f"Content length: {len(article.get('content', ''))} characters")
            print(f"Companies: {article.get('companies', 'N/A')}")
            print(f"Article type: {article.get('article_type', 'N/A')}")
        
        # Save to JSON file
        with open('extracted_articles.json', 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        print(f"\nArticles saved to extracted_articles.json")
    else:
        print("No articles were extracted.")

if __name__ == "__main__":
    main() 