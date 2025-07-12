#!/usr/bin/env python3
"""
Data analysis example for WSJ Adapter.

This example demonstrates how to analyze downloaded articles:
- Content analysis
- Keyword extraction
- Company mention tracking
- Time series analysis
"""

import datetime
import json
import re
from collections import Counter, defaultdict
from wsj_adapter import WSJAdapter
import pandas as pd

def extract_keywords(text, min_length=4, max_words=20):
    """
    Extract keywords from text using simple frequency analysis.
    """
    if not text:
        return []
    
    # Remove common words
    stop_words = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did', 'man', 'men', 'put', 'say', 'she', 'too', 'use', 'with', 'will', 'from', 'have', 'they', 'know', 'want', 'been', 'good', 'much', 'some', 'time', 'very', 'when', 'come', 'here', 'just', 'like', 'long', 'make', 'many', 'over', 'such', 'take', 'than', 'them', 'well', 'were', 'what', 'said', 'each', 'which', 'their', 'would', 'there', 'could', 'other', 'after', 'first', 'never', 'these', 'think', 'where', 'being', 'every', 'great', 'might', 'shall', 'still', 'those', 'under', 'while', 'should', 'years', 'percent', 'million', 'billion', 'according', 'including', 'during', 'through', 'between', 'before', 'after', 'since', 'about', 'above', 'below', 'against', 'among', 'around', 'because', 'since', 'until', 'while', 'during', 'before', 'after', 'above', 'below', 'under', 'over', 'between', 'through', 'across', 'along', 'around', 'behind', 'beside', 'beyond', 'inside', 'outside', 'throughout', 'within', 'without'
    }
    
    # Clean and split text
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    
    # Filter words
    filtered_words = [
        word for word in words 
        if len(word) >= min_length and word not in stop_words
    ]
    
    # Count frequency
    word_counts = Counter(filtered_words)
    
    return word_counts.most_common(max_words)

def analyze_content(articles):
    """
    Perform content analysis on articles.
    """
    print("\n" + "=" * 60)
    print("CONTENT ANALYSIS")
    print("=" * 60)
    
    if not articles:
        print("No articles to analyze.")
        return
    
    # Combine all content
    all_content = []
    headlines = []
    summaries = []
    
    for article in articles:
        content = article.get('content', '')
        headline = article.get('headline', '')
        summary = article.get('summary', '')
        
        if content:
            all_content.append(content)
        if headline:
            headlines.append(headline)
        if summary:
            summaries.append(summary)
    
    # Analyze headlines
    print("\nHEADLINE ANALYSIS")
    print("-" * 30)
    if headlines:
        headline_text = ' '.join(headlines)
        headline_keywords = extract_keywords(headline_text, min_length=3, max_words=10)
        print("Top keywords in headlines:")
        for word, count in headline_keywords:
            print(f"  {word}: {count}")
    
    # Analyze content
    print("\nCONTENT ANALYSIS")
    print("-" * 30)
    if all_content:
        combined_content = ' '.join(all_content)
        content_keywords = extract_keywords(combined_content, max_words=15)
        print("Top keywords in content:")
        for word, count in content_keywords:
            print(f"  {word}: {count}")
    
    # Word count statistics
    print("\nWORD COUNT STATISTICS")
    print("-" * 30)
    word_counts = [len(content.split()) for content in all_content]
    if word_counts:
        print(f"Average words per article: {sum(word_counts) / len(word_counts):.1f}")
        print(f"Shortest article: {min(word_counts)} words")
        print(f"Longest article: {max(word_counts)} words")
        print(f"Total words: {sum(word_counts):,}")

def analyze_companies(articles):
    """
    Analyze company mentions in articles.
    """
    print("\n" + "=" * 60)
    print("COMPANY ANALYSIS")
    print("=" * 60)
    
    company_data = defaultdict(list)
    
    for article in articles:
        companies = article.get('companies', '')
        date = article.get('date', '')
        headline = article.get('headline', '')
        
        if companies:
            for company in companies.split(','):
                company = company.strip()
                if company:
                    company_data[company].append({
                        'date': date,
                        'headline': headline
                    })
    
    if not company_data:
        print("No company data found.")
        return
    
    # Sort companies by mention count
    sorted_companies = sorted(company_data.items(), key=lambda x: len(x[1]), reverse=True)
    
    print(f"Total companies mentioned: {len(sorted_companies)}")
    print("\nTop 10 companies by mention count:")
    for company, mentions in sorted_companies[:10]:
        print(f"  {company}: {len(mentions)} mentions")
    
    # Company mention timeline
    print("\nCOMPANY MENTION TIMELINE")
    print("-" * 30)
    
    date_companies = defaultdict(set)
    for company, mentions in company_data.items():
        for mention in mentions:
            if mention['date']:
                date_companies[mention['date']].add(company)
    
    for date in sorted(date_companies.keys()):
        companies = date_companies[date]
        print(f"  {date}: {len(companies)} companies mentioned")

def create_dataframe(articles):
    """
    Create a pandas DataFrame from articles for analysis.
    """
    print("\n" + "=" * 60)
    print("DATAFRAME ANALYSIS")
    print("=" * 60)
    
    if not articles:
        print("No articles to convert to DataFrame.")
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(articles)
    
    print(f"DataFrame shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Basic statistics
    print("\nBASIC STATISTICS")
    print("-" * 30)
    
    # Content length
    df['content_length'] = df['content'].fillna('').str.len()
    print(f"Average content length: {df['content_length'].mean():.1f}")
    print(f"Median content length: {df['content_length'].median():.1f}")
    
    # Date distribution
    if 'date' in df.columns:
        date_counts = df['date'].value_counts()
        print(f"\nArticles by date:")
        for date, count in date_counts.head().items():
            print(f"  {date}: {count}")
    
    # Headlines with content
    has_content = df['content'].notna() & (df['content'] != '')
    has_headline = df['headline'].notna() & (df['headline'] != '')
    
    print(f"\nData completeness:")
    print(f"  Articles with content: {has_content.sum()}")
    print(f"  Articles with headlines: {has_headline.sum()}")
    print(f"  Complete articles: {(has_content & has_headline).sum()}")
    
    return df

def main():
    """
    Main function for data analysis example.
    """
    print("WSJ Adapter - Data Analysis Example")
    print("=" * 60)
    
    # Initialize adapter
    adapter = WSJAdapter(
        start_date=datetime.date(2024, 1, 1),
        end_date=datetime.date(2024, 1, 5),
        topics=['/business/', '/finance/', '/tech/'],
        max_workers=3,
        latest_records=True,
        latest_articles=True
    )
    
    print(f"Configured for date range: {adapter.start_date} to {adapter.end_date}")
    print(f"Topics: {adapter.topics}")
    
    # Download articles
    try:
        print("\nDownloading articles...")
        articles = adapter.download()
        print(f"Successfully downloaded {len(articles)} articles")
        
        if not articles:
            print("No articles downloaded. Exiting.")
            return
        
        # Perform analyses
        analyze_content(articles)
        analyze_companies(articles)
        
        # Create DataFrame analysis
        df = create_dataframe(articles)
        
        # Save results
        print("\n" + "=" * 60)
        print("SAVING RESULTS")
        print("=" * 60)
        
        # Save raw data
        with open('analysis_results.json', 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        print("Raw data saved to analysis_results.json")
        
        # Save DataFrame if available
        if df is not None:
            df.to_csv('analysis_results.csv', index=False)
            print("DataFrame saved to analysis_results.csv")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        return
    
    print("\nData analysis example completed!")

if __name__ == "__main__":
    main() 