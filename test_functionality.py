#!/usr/bin/env python3
"""
Simple test script to verify the WSJ adapter functionality.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from wsj_adapter.wsj_adapter import (
    extract_article_content, 
    extract_newsletter_content,
    extract_single_article_content,
    process_article_url
)
from bs4 import BeautifulSoup

def test_newsletter_extraction():
    """Test newsletter content extraction."""
    print("Testing newsletter content extraction...")
    
    # Sample newsletter HTML
    newsletter_html = '''
    <table>
        <tr>
            <td class="email-body__space">
                <h1>Supply Chain Strategies</h1>
            </td>
        </tr>
        <tr>
            <td class="email-body__article">
                <p><strong>The Covid-19 recovery in Europe is raising new healthcare supply-chain concerns.</strong> 
                European countries are reporting shortages of amoxicillin and other widely used antibiotics.</p>
            </td>
        </tr>
        <tr>
            <td class="email-body__space">
                <h1>Number of the Day</h1>
            </td>
        </tr>
        <tr>
            <td class="big-num__txt">
                <p>Overall U.S. container imports in November, down 12% from October.</p>
            </td>
        </tr>
    </table>
    '''
    
    soup = BeautifulSoup(newsletter_html, 'html.parser')
    articles = extract_newsletter_content(soup)
    
    print(f"Found {len(articles)} articles in newsletter")
    for i, article in enumerate(articles):
        print(f"  Article {i+1}: {article['headline']} ({len(article['content'])} chars)")
    
    return len(articles) == 2

def test_single_article_extraction():
    """Test single article content extraction."""
    print("\nTesting single article content extraction...")
    
    # Sample single article HTML
    article_html = '''
    <html>
        <head>
            <meta name="description" content="Test article summary">
            <meta name="keywords" content="test, article">
            <meta name="cXenseParse:recs:wsj-date" content="2024-01-01">
        </head>
        <body>
            <h1 data-testid="headline">Test Article Headline</h1>
            <div data-testid="article-content">
                <p>This is the first paragraph of the article content.</p>
                <p>This is the second paragraph with more detailed information.</p>
            </div>
        </body>
    </html>
    '''
    
    soup = BeautifulSoup(article_html, 'html.parser')
    articles = extract_article_content(soup)
    
    print(f"Found {len(articles)} articles")
    if articles:
        article = articles[0]
        print(f"  Headline: {article['headline']}")
        print(f"  Summary: {article['summary']}")
        print(f"  Content length: {len(article['content'])} chars")
    
    return len(articles) == 1

def test_unified_extraction():
    """Test the unified extraction function."""
    print("\nTesting unified extraction function...")
    
    # Test with newsletter HTML
    newsletter_html = '''
    <table>
        <tr>
            <td class="email-body__article">
                <h1>Test Newsletter Article</h1>
                <p>This is newsletter content.</p>
            </td>
        </tr>
    </table>
    '''
    
    soup = BeautifulSoup(newsletter_html, 'html.parser')
    articles = extract_article_content(soup)
    
    print(f"Unified extraction found {len(articles)} articles")
    return len(articles) > 0

def main():
    """Run all tests."""
    print("WSJ Adapter Functionality Tests")
    print("=" * 40)
    
    tests = [
        test_newsletter_extraction,
        test_single_article_extraction,
        test_unified_extraction
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                print("✓ PASSED")
                passed += 1
            else:
                print("✗ FAILED")
        except Exception as e:
            print(f"✗ FAILED with error: {e}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! The WSJ adapter is working correctly.")
    else:
        print("Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    main() 