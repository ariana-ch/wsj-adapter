import datetime
import json
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor
from logging import getLogger, StreamHandler, INFO
from typing import List, Optional, Dict

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter, Retry


def _get_logger(name: str = __name__):
    # Configure logging
    logger = getLogger(name)
    logger.setLevel(INFO)
    handler = StreamHandler()
    handler.setLevel(INFO)
    logger.addHandler(handler)
    logger.propagate = False
    return logger


logger = _get_logger('WSJAdapter')

TOPICS = ['',
          '/opinion/',
          '/business/',
          '/economy/',
          '/finance/',
          '/politics/',
          '/us-news/',
          '/news/',
          '/tech/',
          '/world/',
          '/market-data/',
          '/news/business/',
          '/news/latest/',
          '/news/markets/',
          '/news/tech/',
          '/news/us/']

EXCLUDE_PATTERNS = ['signin', 'login', 'subscri', 'member', 'footer', 'about', 'contact', 'privacy', 'terms', 'help',
                    'video', 'podcast', 'audio', '-worship', 'architecture', 'lifestyle', 'fashion', 'on-the-clock',
                    'recipes', 'travel', 'real-estate', 'science', 'health', 'sports', 'arts-culture', 'art-review',
                    'obituar', 'wine', 'film-review', 'book-review', 'television-review', 'arts', 'art', '-review',
                    'bookshelf', 'play.google', 'apple.com/us/app', 'policy/legal-policies', 'djreprints', 'register',
                    'wsj.jobs', 'smartmoney', 'classifieds', 'cultural', 'masterpiece', 'puzzle', 'personal-finance',
                    'style', 'customercenter', 'snapchat', 'cookie-notice', 'facebook', 'instagram', 'twitter',
                    '/policy/copyright-policy', '/policy/data-policy', 'market-data/quotes/'
                    'accessibility-statement', 'press-room', 'mansionglobal', 'images', 'mailto', 'youtube', '#']


def safe_get(url: str, session: requests.Session, timeout: int = 10) -> Optional[requests.Response]:
    """
    GET with retries configured on the session,
    plus a randomized sleep to throttle.
    Returns None if all retries fail.
    """
    # Throttle - this sleep is per-thread, so for parallel calls, it means each thread waits.
    time.sleep(random.uniform(1.0, 2.0))  # Increased sleep for better etiquette
    logger.debug(f"GET {url}")
    try:
        resp = session.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp
    except requests.RequestException as e:
        logger.error(f"GET {url} failed with exception: {e}")
        return None


def create_session() -> requests.Session:
    """
    Create a safe session for GET requests.
    This session will be shared across threads to enable connection pooling.
    """
    session = requests.Session()
    # Increased total retries and backoff factor for more resilience
    retries = Retry(
        total=5,  # Reduced retries
        backoff_factor=1,  # 1s, 2s, 4s, 8s, 16s
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def cdx_query(url: str, session: requests.Session, start_date: datetime.date, end_date: datetime.date) -> List[
    List[str]]:
    """
    Query the Wayback Machine's CDX API for a specific URL and date range.

    This function constructs a URL for the CDX API, sends a GET request,
    and returns a list of records containing timestamps and original URLs.
    The records are filtered to include only HTML pages with a status code of 200.
    The results are collapsed by digest to avoid duplicates.
    The function raises a WaybackMachineNoLinks exception if no records are found
    or if the request fails.

    Args:
        url: The URL to query.
        session: A requests.Session object for making HTTP requests.
        start_date: The start date for the query (inclusive).
        end_date: The end date for the query (inclusive).

    Returns:
        A list of records, where each record is a list containing a timestamp and the original URL.
    Raises:
        WaybackMachineNoLinks: If no records are found or if the request fails.
    """
    cdx_url = (
        "https://web.archive.org/cdx/search/cdx"
        f"?url={url}?"
        f"&fl=timestamp,original"
        f"&from={start_date:%Y%m%d}"
        f"&to={end_date:%Y%m%d}"
        "&output=json"
        "&filter=mimetype:text/html"
        "&filter=statuscode:200"
        "&collapse=digest"
    )
    resp = safe_get(cdx_url, session)
    if not resp:
        logger.error(f"Failed to fetch index for URL '{cdx_url}'")

    records = resp.json()[1:]  # skip header row
    if not records:
        logger.warning(f"No records found for URL '{url}'")
    return records


def is_article(url: str) -> bool:
    url = url.rsplit('https://', 1)[-1]
    if not '-' in url:
        return False
    tail = url.rsplit('-', 1)[-1]

    # Check if the URL ends with a valid article ID (at least 3 digits)
    return len(re.compile(r'\d').findall(tail)) > 3


def extract_article_links(soup: BeautifulSoup) -> List[str]:
    """
    Extract all article links from the BeautifulSoup object.
    Focuses on finding actual article URLs, not navigation or other links.
    """
    article_links = []

    # Find all links
    links = soup.find_all('a', href=True)

    for link in links:
        href = link['href']

        # Skip if href is empty or just a fragment
        if (not href or href.startswith('#') or any([pattern in href.lower() for pattern in EXCLUDE_PATTERNS]) or
                not href.startswith('http')):
            continue

        href = href.rsplit('?mod', 1)[0]  # Remove query parameters if any

        # Check if it's an article URL
        if is_article(href):
            article_links.append(href)

    return list(set(article_links))


def extract_single_article_content(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Extract content from a single WSJ article page.
    Returns a dictionary with article data including keywords and cleaned content.
    Handles standard WSJ article pages with stock ticker information and metadata.
    """
    article_data = {
        'headline': '',
        'content': '',
        'summary': '',
        'keywords': '',
        'companies': '',
        'date': ''
    }

    # Extract headline
    headline_selectors = [
        'h1[data-testid="headline"]',
        'h1.WSJTheme--headlineText',
        'h1',
        '[data-testid="headline"]',
        '.WSJTheme--headlineText'
    ]

    for selector in headline_selectors:
        headline_elem = soup.select_one(selector)
        if headline_elem and headline_elem.get_text(strip=True):
            article_data['headline'] = headline_elem.get_text(strip=True)
            break

    # Extract keywords and metadata
    keyword_selectors = ['cXenseParse:wsj-editorial-keyword',
                         'page_editorial_keywords',
                         'keywords']
    for selector in keyword_selectors:
        keyword_elem = soup.find('meta', attrs={'name': selector})
        if keyword_elem and keyword_elem.get('content'):
            article_data['keywords'] = keyword_elem.get('content')
            break

    summary_selectors = ['description',
                         'cXenseParse:recs:wsj-summary']
    # Extract description
    for selector in summary_selectors:
        summary_elem = soup.find('meta', attrs={'name': selector})
        if summary_elem and summary_elem.get('content'):
            article_data['summary'] = summary_elem.get('content')
            break

    date_selectors = ['cXenseParse:recs:wsj-date',
                      'article.published']
    for selector in date_selectors:
        date_elem = soup.find('meta', attrs={'name': selector})
        if date_elem and date_elem.get('content'):
            date = date_elem.get('content')
            date = re.compile(r'\d{4}-\d{2}-\d{2}').findall(date)
            if date:
                article_data['date'] = date[0]
                break

    # Extract and clean stock ticker information
    stock_tickers = []
    stock_elements = soup.find_all('span', style='display:unset')

    for stock_wrapper in stock_elements:
        # Extract company name
        company_link = stock_wrapper.find('a', {'data-type': 'company'})
        if not company_link:
            continue

        company_name = company_link.get_text().strip()

        # Extract ticker symbol and percentage
        ticker_link = stock_wrapper.find('a', class_=lambda x: x and 'ChicletStyle' in x)
        if ticker_link:
            # Extract ticker symbol (usually the first part before percentage)
            ticker_text = ticker_link.get_text().strip()

            # Extract percentage change
            percent_span = ticker_link.find('span', class_=lambda x: x and 'ChicletChange' in x)
            if percent_span:
                percent_text = percent_span.get_text().strip()

                # Extract direction
                hidden_label = ticker_link.find('span', class_=lambda x: x and 'ArrowHiddenLabel' in x)
                direction = 'change'
                if hidden_label:
                    direction_text = hidden_label.get_text().strip().lower()
                    if 'increase' in direction_text:
                        direction = 'gain'
                    elif 'decrease' in direction_text:
                        direction = 'drop'

                ticker_symbol = ticker_text.split()[0] if ticker_text else ''
                formatted_ticker = f"{company_name} {ticker_symbol} ({percent_text} {direction})"
                stock_tickers.append(formatted_ticker)

    article_data['companies'] = ','.join(stock_tickers)

    # Extract content with better cleaning
    content_selectors = [
        '[data-testid="article-content"]',
        '.WSJTheme--bodyText',
        '.article-content',
        'article p',
        '.content p'
    ]

    content_paragraphs = []
    for selector in content_selectors:
        paragraphs = soup.select(selector)
        if paragraphs:
            for p in paragraphs:
                text = p.get_text(separator=" ", strip=True)
                # Skip short paragraphs, copyright notices, and URLs
                if (len(text) > 50 and
                        not text.startswith('Copyright ©') and
                        not text.startswith('https://') and
                        not text.startswith('This copy is for your personal') and
                        not text.startswith('By')
                ):
                    content_paragraphs.append(text)
            if content_paragraphs:
                break

    # Clean up stock ticker formatting in content
    if content_paragraphs:
        cleaned_content = []
        for paragraph in content_paragraphs:
            cleaned_paragraph = paragraph

            # Replace messy stock ticker text with clean format
            for ticker in stock_tickers:
                # Extract parts for replacement
                parts = ticker.split(' (')
                if len(parts) == 2:
                    company_ticker = parts[0]  # e.g., "Boeing BA"
                    change_info = parts[1].rstrip(')')  # e.g., "-0.68% drop"

                    # Find and replace the messy version
                    company_name = company_ticker.split()[0]
                    ticker_symbol = company_ticker.split()[1]

                    # Pattern to match messy ticker format
                    messy_pattern = rf'{company_name}\s*{ticker_symbol}\s*[-+]?\d+\.?\d*%[^.]*triangle'
                    cleaned_paragraph = re.sub(messy_pattern, ticker, cleaned_paragraph)

            cleaned_content.append(cleaned_paragraph)

        article_data['content'] = '\n\n'.join(cleaned_content)

    # If no summary from metadata, create from content
    if not article_data['summary'] and article_data['content']:
        sentences = article_data['content'].split('. ')
        if sentences:
            article_data['summary'] = '. '.join(sentences[:3]) + '.'

    return article_data


def extract_newsletter_content(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """
    Extract content from WSJ email newsletter formats that contain multiple articles.
    Returns a list of article dictionaries, each containing headline, content, and metadata.
    Handles WSJ newsletter formats like Logistics Report, etc.
    """
    articles = []
    
    # Check if this looks like an email newsletter format
    email_body_selectors = [
        '.email-body__article',
        'td[class*="email-body"]',
        'table[class*="email"]'
    ]
    
    is_email_newsletter = False
    for selector in email_body_selectors:
        if soup.select(selector):
            is_email_newsletter = True
            break
    
    if not is_email_newsletter:
        # Fall back to single article extraction
        single_article = extract_single_article_content(soup)
        if single_article['headline'] and single_article['content']:
            return [single_article]
        return []
    
    # Extract date from the page if available
    date = ''
    date_patterns = [
        r'(\d{4}-\d{2}-\d{2})',
        r'(\d{1,2}/\d{1,2}/\d{4})',
        r'(\w+ \d{1,2}, \d{4})'
    ]
    
    page_text = soup.get_text()
    for pattern in date_patterns:
        match = re.search(pattern, page_text)
        if match:
            date = match.group(1)
            break
    
    # Find all h1 elements which typically mark article sections in newsletters
    h1_elements = soup.find_all('h1')
    
    for i, h1 in enumerate(h1_elements):
        headline = h1.get_text(strip=True)
        if not headline or len(headline) < 3:
            continue
            
        # Skip common newsletter section headers that aren't articles
        skip_headers = ['about us', 'unsubscribe', 'privacy policy', 'contact us', 'follow us']
        if any(skip_header in headline.lower() for skip_header in skip_headers):
            continue
        
        # Find the content associated with this headline
        content_td = None
        
        # Strategy 1: Look for content between this h1 and the next h1
        next_h1 = None
        if i + 1 < len(h1_elements):
            next_h1 = h1_elements[i + 1]
        
        # Look for email-body__article td between this h1 and next h1
        current_element = h1
        while current_element and current_element != next_h1:
            # Look for the next td with email-body__article class
            next_article_td = current_element.find_next('td', class_=lambda x: x and 'email-body__article' in x)
            if next_article_td:
                # Check if this td comes before the next h1
                if not next_h1 or next_article_td.find_previous('h1') == h1:
                    content_td = next_article_td
                    break
            
            # Also look for td with big-num__txt class (for "Number of the Day" sections)
            next_num_td = current_element.find_next('td', class_=lambda x: x and 'big-num__txt' in x)
            if next_num_td:
                # Check if this td comes before the next h1
                if not next_h1 or next_num_td.find_previous('h1') == h1:
                    content_td = next_num_td
                    break
            
            # Move up to parent and try again
            current_element = current_element.parent
            if not current_element or current_element.name == 'body':
                break
        
        # Strategy 2: If no content found, look for any paragraph content that follows this h1
        if not content_td:
            current_element = h1
            for _ in range(15):  # Look up to 15 levels up and forward
                if current_element:
                    # Look for paragraphs that come after this h1
                    paragraphs = current_element.find_all_next('p', limit=5)
                    for p in paragraphs:
                        # Check if this paragraph comes before the next h1
                        if not next_h1 or p.find_previous('h1') == h1:
                            text = p.get_text(strip=True)
                            if len(text) > 20 and not text.startswith('Copyright'):
                                content_td = p
                                break
                    if content_td:
                        break
                    current_element = current_element.parent
                else:
                    break
        
        if content_td:
            # Extract and clean the content
            if content_td.name == 'td':
                # For td elements, get all paragraphs
                paragraphs = content_td.find_all('p')
                if paragraphs:
                    content_parts = []
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        if text and len(text) > 10:
                            content_parts.append(text)
                    content_text = ' '.join(content_parts)
                else:
                    content_text = content_td.get_text(separator=" ", strip=True)
            else:
                content_text = content_td.get_text(separator=" ", strip=True)
            
            # Clean up the content
            if content_text:
                # Remove common newsletter artifacts
                content_text = re.sub(r'\([^)]*\)', '', content_text)  # Remove parenthetical citations
                content_text = re.sub(r'https?://[^\s]+', '', content_text)  # Remove URLs
                content_text = re.sub(r'\s+', ' ', content_text)  # Normalize whitespace
                content_text = content_text.strip()
                
                # Skip if content is too short or looks like navigation
                if (len(content_text) > 50 and 
                    not content_text.startswith('Follow') and
                    not content_text.startswith('Reach') and
                    not content_text.startswith('Copyright')):
                    
                    # Create article data
                    article_data = {
                        'headline': headline,
                        'content': content_text,
                        'summary': content_text[:200] + '...' if len(content_text) > 200 else content_text,
                        'keywords': '',
                        'companies': '',
                        'date': date,
                        'article_type': 'newsletter_section'
                    }
                    
                    # Extract company names from content (look for bold text)
                    companies = []
                    bold_elements = content_td.find_all(['strong', 'b'])
                    for bold in bold_elements:
                        company_name = bold.get_text(strip=True)
                        if company_name and len(company_name) > 1 and len(company_name) < 50:
                            # Filter out very long bold text that's likely not a company name
                            companies.append(company_name)
                    
                    article_data['companies'] = ', '.join(set(companies))
                    
                    articles.append(article_data)
    
    # If no articles found with h1 method, try alternative approach
    if not articles:
        # Look for all td elements with email-body__article class
        article_tds = soup.find_all('td', class_=lambda x: x and 'email-body__article' in x)
        
        for td in article_tds:
            paragraphs = td.find_all('p')
            if paragraphs:
                # Combine all paragraphs in this section
                content_parts = []
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if len(text) > 20 and not text.startswith('Copyright'):
                        content_parts.append(text)
                
                if content_parts:
                    content_text = ' '.join(content_parts)
                    content_text = re.sub(r'\s+', ' ', content_text).strip()
                    
                    if len(content_text) > 100:
                        # Try to extract a headline from the first sentence or create a generic one
                        first_sentence = content_text.split('.')[0] + '.'
                        headline = first_sentence[:100] + '...' if len(first_sentence) > 100 else first_sentence
                        
                        article_data = {
                            'headline': headline,
                            'content': content_text,
                            'summary': content_text[:200] + '...' if len(content_text) > 200 else content_text,
                            'keywords': '',
                            'companies': '',
                            'date': date,
                            'article_type': 'newsletter_content'
                        }
                        
                        articles.append(article_data)
    
    return articles


def extract_article_content(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """
    Intelligently extract article content from WSJ pages.
    Automatically detects whether the page is a single article or a newsletter format
    and uses the appropriate extraction method.
    Returns a list of article dictionaries.
    """
    # Try newsletter extraction first (it will fall back to single article if needed)
    return extract_newsletter_content(soup)


def process_article_url(url: str, session: requests.Session) -> Optional[List[Dict]]:
    """
    Process a single article URL to extract its content.
    Returns a list of article data if successful, None otherwise.
    Handles both single articles and newsletter formats with multiple articles.
    """
    try:
        response = safe_get(url, session)
        if not response:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Use the unified extraction function
        articles = extract_article_content(soup)
        
        if articles:
            # Add URL and timestamp to each article
            timestamp = re.findall(r'\d{14}', url)
            for article in articles:
                article['url'] = url
                article['timestamp'] = timestamp[0] if timestamp else ''
                article['archive_url'] = url
            return articles

        return None

    except Exception as e:
        logger.error(f"Error processing article {url}: {e}")
        return None


def process_cdx_record(record: List[str], shared_session: requests.Session) -> Optional[List[Dict]]:
    """
    Processes a single CDX record, fetches the archived page, extracts article links,
    and then processes each article to extract content.
    """
    timestamp, website = record
    url = f'https://web.archive.org/web/{timestamp}/{website}'
    logger.info(f"Processing record: {url}")

    response = safe_get(url, shared_session)
    if not response:
        logger.error(f"Failed to fetch main archived page at {url}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    article_links = extract_article_links(soup)

    if not article_links:
        logger.warning(f"No article links found in the archived page at {url}")
        return None

    logger.info(f"Found {len(article_links)} article links in {url}")

    # Process articles (limit to first 10 to avoid overwhelming)
    articles = []
    for i, article_url in enumerate(article_links[:10]):
        logger.info(f"Processing article {i + 1}/{min(len(article_links), 10)}: {article_url}")
        article_results = process_article_url(article_url, shared_session)
        if article_results:
            # article_results is now a list, so extend instead of append
            articles.extend(article_results)

    logger.info(f"Successfully extracted {len(articles)} articles from {url}")
    return articles


class WSJAdapter:
    def __init__(self, start_date: datetime.date, end_date: datetime.date, topics: list = TOPICS,
                 max_workers: int = 3, latest_records: bool = False, latest_articles: bool = False):
        self.url = 'www.wsj.com'
        self.start_date = start_date
        self.end_date = end_date
        self.topics = topics
        self.max_workers = max_workers
        self.latest_records = latest_records
        self.latest_articles = latest_articles
        self.session = create_session()
        self.records = None
        self.article_links = None

    def get_all_records(self) -> List[List[str]]:
        logger.info(f'Retrieving records from:\n{"\n".join([f"www.wsj.com{topic}" for topic in self.topics])}')
        records = []
        for topic in self.topics:
            records.extend(cdx_query(url=f'www.wsj.com{topic}', session=self.session, start_date=self.start_date,
                                     end_date=self.end_date))
        if self.latest_records:
            # If latest_records is True, filter to keep only the latest record for each day
            df = pd.DataFrame(records, columns=['timestamp', 'original'])
            df['datetime'] = pd.to_datetime(df['timestamp'], format='%Y%m%d%H%M%S')
            df['date'] = df['datetime'].dt.date
            df = df.sort_values(by='datetime')
            df['clean_url'] = df.original.apply(lambda x: '/'.join(
                [i.strip() for i in x.replace('http://', '').replace('https://', '').split('/') if i.strip()]))
            df = df.groupby(['date', 'clean_url'], as_index=False).last()
            records = df[['timestamp', 'original']].values.tolist()

        return records


    def get_all_article_links(self, records: List[List[str]]) -> List[str]:
        """
        Fetch all article links from the Wayback Machine for the specified URL and date range.
        This method retrieves CDX records and processes each record to extract article links.
        """

        def _do_get_article_links(record) -> Optional[List[str]]:
            timestamp, website = record

            archive_url = f'https://web.archive.org/web/{timestamp}/{website}'
            response = safe_get(archive_url, self.session)
            if not response:
                return None

            soup = BeautifulSoup(response.text, "html.parser")
            links = list(set(extract_article_links(soup)))
            return links

        logger.info(f"Fetching all article links between {self.start_date} and {self.end_date}")

        all_links = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(_do_get_article_links, record) for record in records]

            for future in futures:
                result = future.result()
                if result:
                    all_links.extend(result)
        #
        # for record in records:
        #     timestamp, website = record
        #
        #     archive_url = f'https://web.archive.org/web/{timestamp}/{website}'
        #     response = safe_get(archive_url, self.session)
        #     if not response:
        #         continue
        #
        #     soup = BeautifulSoup(response.text, "html.parser")
        #     links = list(set(extract_article_links(soup)))
        #     all_links.extend(links)

        if self.latest_articles:
            # If latest_articles is True, filter to keep only the latest link for each day
            df = pd.DataFrame(all_links, columns=['url'])
            df['date'] = pd.to_datetime(df['url'].str.extract(r'(\d{8})')[0], format='%Y%m%d')
            df['article_url'] = df.url.apply(lambda x: x.rsplit('https://', 1)[-1])
            df = df.sort_values(by='date')
            df = df.groupby(['date', 'article_url'], as_index=False).last()
            all_links = df['url'].tolist()
        logger.info(f"Found {len(all_links)} article links from between {self.start_date} and {self.end_date}")
        return list(set(all_links))

    def download(self) -> List[Dict]:
        logger.info(f"Starting download for {self.url} from {self.start_date} to {self.end_date}")
        records = self.get_all_records()
        self.records = records

        logger.info(f"Retrieved {len(records)} CDX records")
        article_links = self.get_all_article_links(records)
        self.article_links = article_links

        if not article_links:
            logger.error(f"Could not retrieve any article links")
            return []

        all_articles = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(process_article_url, link, self.session) for link in article_links]

            for future in futures:
                result = future.result()
                if result:
                    # result is now a list, so extend instead of append
                    all_articles.extend(result)
        logger.info(f"Successfully extracted {len(all_articles)} articles")
        logger.info(f"Finished processing. Total articles extracted: {len(all_articles)}")
        return all_articles


if __name__ == "__main__":
    # Test with a smaller date range and fewer workers
    wb = WSJAdapter(
        latest_records=True,
        latest_articles=True,
        start_date=datetime.date(2022, 12, 1),
        end_date=datetime.date(2022, 12, 31),  # Just one day
        max_workers=5  # Reduced workers
    )
    '''
    Found 289 article links from between 2022-12-01 and 2022-12-31
    '''
    downloaded_articles = wb.download()

    # Print summary
    print(f"\n--- Download Summary ---")
    print(f"Total articles extracted: {len(downloaded_articles)}")

    # Print first few articles as examples
    for i, article in enumerate(downloaded_articles[:3]):
        print(f"\n--- Article {i + 1} ---")
        print(f"Headline: {article.get('headline', 'N/A')}")
        print(f"Author: {article.get('author', 'N/A')}")
        print(f"Date: {article.get('date', 'N/A')}")
        print(f"URL: {article.get('url', 'N/A')}")
        print(f"Summary: {article.get('summary', 'N/A')[:200]}...")
        print(f"Content length: {len(article.get('content', ''))} characters")

    # Save to JSON file
    if downloaded_articles:
        with open('extracted_articles_new.json', 'w', encoding='utf-8') as f:
            json.dump(downloaded_articles, f, indent=2, ensure_ascii=False)
        print(f"\nArticles saved to extracted_articles.json")
