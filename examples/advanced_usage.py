#!/usr/bin/env python3
"""
Advanced usage example for WSJ Adapter.

This example demonstrates advanced features including:
- Custom topic selection
- Working with larger date ranges
- Accessing raw CDX records
- Processing and analyzing results
"""

import datetime
import json
from collections import Counter
from wsj_adapter import WSJAdapter, TOPICS

def analyze_articles(articles):
    """
    Analyze downloaded articles and print statistics.
    """
    print("\n" + "=" * 50)
    print("ARTICLE ANALYSIS")
    print("=" * 50)
    
    if not articles:
        print("No articles to analyze.")
        return
    
    # Basic statistics
    print(f"Total articles: {len(articles)}")
    
    # Articles with content
    articles_with_content = [a for a in articles if a.get('content')]
    print(f"Articles with content: {len(articles_with_content)}")
    
    # Date distribution
    dates = [a.get('date') for a in articles if a.get('date')]
    if dates:
        date_counts = Counter(dates)
        print(f"\nArticles by date:")
        for date, count in sorted(date_counts.items()):
            print(f"  {date}: {count} articles")
    
    # Companies mentioned
    companies = []
    for article in articles:
        if article.get('companies'):
            companies.extend(article['companies'].split(','))
    
    if companies:
        company_counts = Counter(companies)
        print(f"\nTop 5 companies mentioned:")
        for company, count in company_counts.most_common(5):
            print(f"  {company.strip()}: {count} times")
    
    # Average content length
    content_lengths = [len(a.get('content', '')) for a in articles_with_content]
    if content_lengths:
        avg_length = sum(content_lengths) / len(content_lengths)
        print(f"\nAverage article length: {avg_length:.0f} characters")
        print(f"Shortest article: {min(content_lengths)} characters")
        print(f"Longest article: {max(content_lengths)} characters")

def save_results(articles, filename="wsj_articles.json"):
    """
    Save articles to JSON file.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to {filename}")
    except Exception as e:
        print(f"Error saving results: {e}")

def main():
    """
    Advanced example demonstrating multiple features.
    """
    print("WSJ Adapter - Advanced Usage Example")
    print("=" * 50)
    
    # Example 1: Custom topic selection
    print("\n1. Custom Topic Selection")
    print("-" * 30)
    
    # Select specific topics
    custom_topics = ['/business/', '/finance/', '/tech/']
    
    adapter = WSJAdapter(
        start_date=datetime.date(2024, 1, 1),
        end_date=datetime.date(2024, 1, 3),
        topics=custom_topics,
        max_workers=3,
        latest_records=True,
        latest_articles=True
    )
    
    print(f"Using custom topics: {custom_topics}")
    print(f"Available topics: {TOPICS}")
    
    # Example 2: Get raw CDX records first
    print("\n2. Working with Raw CDX Records")
    print("-" * 30)
    
    try:
        records = adapter.get_all_records()
        print(f"Found {len(records)} CDX records")
        
        if records:
            print("Sample record:")
            print(f"  Timestamp: {records[0][0]}")
            print(f"  URL: {records[0][1]}")
        
        # Get article links without downloading content
        article_links = adapter.get_all_article_links(records)
        print(f"Found {len(article_links)} article links")
        
    except Exception as e:
        print(f"Error getting records: {e}")
        return
    
    # Example 3: Download and analyze
    print("\n3. Download and Analysis")
    print("-" * 30)
    
    try:
        articles = adapter.download()
        print(f"Downloaded {len(articles)} articles")
        
        # Analyze results
        analyze_articles(articles)
        
        # Save results
        save_results(articles, "advanced_example_results.json")
        
    except Exception as e:
        print(f"Error during download: {e}")
        return
    
    # Example 4: Different configurations
    print("\n4. Configuration Comparison")
    print("-" * 30)
    
    # Compare different settings
    configs = [
        {
            'name': 'Latest Only',
            'latest_records': True,
            'latest_articles': True,
            'max_workers': 2
        },
        {
            'name': 'All Records',
            'latest_records': False,
            'latest_articles': False,
            'max_workers': 1
        }
    ]
    
    for config in configs:
        print(f"\nConfiguration: {config['name']}")
        
        test_adapter = WSJAdapter(
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 1, 1),  # Single day
            topics=['/business/'],  # Single topic
            max_workers=config['max_workers'],
            latest_records=config['latest_records'],
            latest_articles=config['latest_articles']
        )
        
        try:
            test_records = test_adapter.get_all_records()
            print(f"  Records found: {len(test_records)}")
            
            if test_records:
                test_links = test_adapter.get_all_article_links(test_records)
                print(f"  Article links: {len(test_links)}")
                
        except Exception as e:
            print(f"  Error: {e}")
    
    print("\nAdvanced usage example completed!")

if __name__ == "__main__":
    main() 