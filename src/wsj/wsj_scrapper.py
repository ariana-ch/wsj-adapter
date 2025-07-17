"""
WSJ Scrapper - A package to download articles from the Wall Street Journal via the Wayback Machine.

This module provides the WSJScrapper class which allows you to:
- Query the Wayback Machine for archived WSJ pages
- Extract article links from those pages
- Download and parse article content
- Handle multiple topics and date ranges
"""

import datetime
import time
import random
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from typing import List, Dict, Optional, Any

# Predefined topics for WSJ sections
TOPICS = [
    '',  # Main page
    '/opinion/',
    '/business/',
    '/economy/',
    '/finance/',
    '/politics/',
    '/us-news/',
    '/news/',
    '/tech/',
    '/world/'
]

# Patterns to exclude from article extraction
EXCLUDE_PATTERNS = [
    '/signin',
    '/subscribe',
    '/login',
    '/register',
    '/about',
    '/contact',
    '/privacy',
    '/terms',
    '/help',
    '/feedback'
]


def create_session() -> requests.Session:
    """Create a requests session with proper configuration."""
    session = requests.Session()
    
    # Set headers to mimic a real browser
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    
    # Configure adapters for connection pooling
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=10,
        pool_maxsize=10,
        max_retries=3,
        pool_block=False
    )
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    return session


def safe_get(url: str, session: requests.Session) -> Optional[requests.Response]:
    """Safely make a GET request with rate limiting and error handling."""
    try:
        # Add random delay to be respectful to the server
        time.sleep(random.uniform(1, 2))
        
        response = session.get(url, timeout=30)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def cdx_query(url: str, start_date: str, end_date: str, session: requests.Session) -> List[Dict[str, str]]:
    """Query the Wayback Machine CDX API for archived pages."""
    cdx_url = "https://web.archive.org/cdx/search/cdx"
    
    params = {
        'url': url,
        'from': start_date,
        'to': end_date,
        'output': 'json',
        'fl': 'timestamp,original',
        'collapse': 'timestamp:8',  # Collapse by day
        'limit': '10000'
    }
    
    try:
        response = safe_get(f"{cdx_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}", session)
        if response is None:
            return []
        
        data = response.json()
        if not data or len(data) <= 1:  # First row is header
            return []
        
        # Convert to list of dictionaries
        records = []
        for row in data[1:]:  # Skip header
            if len(row) >= 2:
                records.append({
                    'timestamp': row[0],
                    'original': row[1]
                })
        
        return records
    except Exception as e:
        print(f"Error querying CDX API: {e}")
        return []


def is_article(url: str) -> bool:
    """Check if a URL is likely an article URL."""
    # WSJ article URLs typically have the pattern: /articles/name-with-dashes-12345678
    article_pattern = r'/articles/[^/]+-\d{8,}'
    return bool(re.search(article_pattern, url))


def extract_article_links(soup: BeautifulSoup) -> List[str]:
    """Extract article links from a BeautifulSoup object."""
    links = []
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        
        # Convert relative URLs to absolute
        if href.startswith('/'):
            href = f"https://www.wsj.com{href}"
        elif not href.startswith('http'):
            continue
        
        # Check if it's an article URL
        if is_article(href):
            # Check if it should be excluded
            if not any(pattern in href for pattern in EXCLUDE_PATTERNS):
                links.append(href)
    
    return list(set(links))  # Remove duplicates


def extract_article_content(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """Extract article content from a BeautifulSoup object."""
    articles = []
    
    # Try to extract single article content first
    headline_elem = soup.find('h1', {'data-testid': 'headline'})
    content_elem = soup.find('div', {'data-testid': 'article-content'})
    
    if headline_elem and content_elem:
        # Single article format
        headline = headline_elem.get_text(strip=True)
        content = content_elem.get_text(strip=True)
        
        # Extract metadata
        summary = ""
        keywords = ""
        date = ""
        
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc:
            summary = meta_desc.get('content', '')
        
        meta_keywords = soup.find('meta', {'name': 'keywords'})
        if meta_keywords:
            keywords = meta_keywords.get('content', '')
        
        meta_date = soup.find('meta', {'name': 'cXenseParse:recs:wsj-date'})
        if meta_date:
            date = meta_date.get('content', '')
        
        articles.append({
            'headline': headline,
            'content': content,
            'summary': summary,
            'keywords': keywords,
            'date': date,
            'article_type': 'single'
        })
    else:
        # Try newsletter format
        newsletter_articles = soup.find_all('td', class_='email-body__article')
        if newsletter_articles:
            for article in newsletter_articles:
                # Find the preceding headline
                headline_elem = article.find_previous('h1')
                headline = headline_elem.get_text(strip=True) if headline_elem else "Newsletter Article"
                
                content = article.get_text(strip=True)
                
                articles.append({
                    'headline': headline,
                    'content': content,
                    'summary': content[:200] + "..." if len(content) > 200 else content,
                    'keywords': "",
                    'date': "",
                    'article_type': 'newsletter'
                })
    
    return articles


def _calculate_content_quality(content_list: List[Dict[str, str]]) -> float:
    """Calculate the quality score of extracted content."""
    if not content_list:
        return 0.0
    
    total_score = 0.0
    for content in content_list:
        score = 0.0
        
        # Score based on content length
        content_text = content.get('content', '')
        if len(content_text) > 1000:
            score += 0.4
        elif len(content_text) > 500:
            score += 0.2
        elif len(content_text) > 100:
            score += 0.1
        
        # Score based on headline presence
        if content.get('headline'):
            score += 0.3
        
        # Score based on summary presence
        if content.get('summary'):
            score += 0.2
        
        # Score based on date presence
        if content.get('date'):
            score += 0.1
        
        total_score += score
    
    return total_score / len(content_list)


def process_article_url(url: str, session: requests.Session) -> Optional[Dict[str, Any]]:
    """Process a single article URL and extract its content."""
    try:
        response = safe_get(url, session)
        if response is None:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        content_list = extract_article_content(soup)
        
        if not content_list:
            return None
        
        # Get the best quality content
        best_content = max(content_list, key=lambda x: len(x.get('content', '')))
        
        # Extract additional metadata
        companies = ""
        # Look for stock ticker patterns in the content
        ticker_pattern = r'\$[A-Z]{1,5}'
        tickers = re.findall(ticker_pattern, best_content.get('content', ''))
        if tickers:
            companies = ", ".join(set(tickers))
        
        # Get the original URL from the Wayback Machine URL
        original_url = url.replace('https://web.archive.org/web/', '')
        original_url = original_url.split('/')[1] if '/' in original_url else url
        
        return {
            'headline': best_content.get('headline', ''),
            'content': best_content.get('content', ''),
            'summary': best_content.get('summary', ''),
            'keywords': best_content.get('keywords', ''),
            'companies': companies,
            'date': best_content.get('date', ''),
            'url': original_url,
            'timestamp': url.split('/')[2] if len(url.split('/')) > 2 else '',
            'archive_url': url,
            'article_type': best_content.get('article_type', 'unknown')
        }
        
    except Exception as e:
        print(f"Error processing article URL {url}: {e}")
        return None


class WSJScrapper:
    """
    A scraper for downloading articles from the Wall Street Journal via the Wayback Machine.
    
    This class provides functionality to:
    - Query the Wayback Machine for archived WSJ pages
    - Extract article links from those pages
    - Download and parse article content
    - Handle multiple topics and date ranges with parallel processing
    """
    
    def __init__(
        self,
        start_date: datetime.date,
        end_date: datetime.date,
        topics: Optional[List[str]] = None,
        max_workers: int = 3,
        no_of_captures: int = 10,
        latest_records: bool = False,
        latest_articles: bool = False
    ):
        """
        Initialize the WSJ Scrapper.
        
        Args:
            start_date: Start date for the search range
            end_date: End date for the search range
            topics: List of WSJ topics to search (default: all topics)
            max_workers: Maximum number of concurrent workers
            no_of_captures: Number of captures to sample per day per topic
            latest_records: If True, get only the latest record per day
            latest_articles: If True, get only the latest article per day
        """
        self.start_date = start_date
        self.end_date = end_date
        self.topics = topics if topics is not None else TOPICS
        self.max_workers = max_workers
        self.no_of_captures = no_of_captures
        self.latest_records = latest_records
        self.latest_articles = latest_articles
        self.url = 'www.wsj.com'
        self.session = create_session()
    
    def get_all_records(self) -> List[Dict[str, str]]:
        """Get all CDX records for the configured date range and topics."""
        all_records = []
        
        for topic in self.topics:
            topic_url = f"{self.url}{topic}"
            start_str = self.start_date.strftime('%Y%m%d')
            end_str = self.end_date.strftime('%Y%m%d')
            
            records = cdx_query(topic_url, start_str, end_str, self.session)
            all_records.extend(records)
        
        return all_records
    
    def get_all_article_links(self, records: List[Dict[str, str]]) -> List[str]:
        """Get all article links from the provided records."""
        all_links = []
        
        for record in records:
            timestamp = record['timestamp']
            original_url = record['original']
            
            # Construct Wayback Machine URL
            wayback_url = f"https://web.archive.org/web/{timestamp}/{original_url}"
            
            response = safe_get(wayback_url, self.session)
            if response is None:
                continue
            
            soup = BeautifulSoup(response.content, 'html.parser')
            links = extract_article_links(soup)
            all_links.extend(links)
        
        return list(set(all_links))  # Remove duplicates
    
    def download(self) -> List[Dict[str, Any]]:
        """
        Download articles from the Wall Street Journal.
        
        Returns:
            List of dictionaries containing article data
        """
        print("Querying Wayback Machine for archived pages...")
        records = self.get_all_records()
        
        if not records:
            print("No archived pages found for the specified date range and topics.")
            return []
        
        print(f"Found {len(records)} archived pages")
        
        print("Extracting article links...")
        article_links = self.get_all_article_links(records)
        
        if not article_links:
            print("No article links found in the archived pages.")
            return []
        
        print(f"Found {len(article_links)} unique article links")
        
        print("Downloading and processing articles...")
        articles = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all article URLs for processing
            future_to_url = {
                executor.submit(process_article_url, url, self.session): url 
                for url in article_links
            }
            
            # Process completed futures
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    article = future.result()
                    if article is not None:
                        articles.append(article)
                        print(f"Successfully processed: {article.get('headline', 'Unknown')[:50]}...")
                except Exception as e:
                    print(f"Error processing {url}: {e}")
        
        print(f"Successfully downloaded {len(articles)} articles")
        return articles 