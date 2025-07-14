"""
Tests for utility functions and edge cases.
"""

import unittest
from unittest.mock import Mock, patch
import datetime
import requests
from bs4 import BeautifulSoup

from wsj_adapter.wsj_adapter import (
    is_article, extract_article_links, extract_article_content,
    TOPICS, EXCLUDE_PATTERNS, safe_get, create_session, _calculate_content_quality
)


class TestIsArticle(unittest.TestCase):
    """Test is_article function with various edge cases."""
    
    def test_valid_article_urls(self):
        """Test valid article URLs."""
        valid_urls = [
            'https://www.wsj.com/articles/test-article-12345678',
            'https://www.wsj.com/business/test-business-article-98765432',
            'https://www.wsj.com/finance/market-news-article-11111111',
            'www.wsj.com/articles/simple-url-format-22222222'
        ]
        
        for url in valid_urls:
            with self.subTest(url=url):
                self.assertTrue(is_article(url), f"Should be valid: {url}")
    
    def test_invalid_article_urls(self):
        """Test invalid article URLs."""
        invalid_urls = [
            'https://www.wsj.com/articles/short-123',  # Too few digits
            'https://www.wsj.com/articles/no-numbers',  # No digits
            'https://www.wsj.com/about',  # No dash
            'https://www.wsj.com/signin',  # Excluded pattern
            'https://www.wsj.com/articles/test-12',  # Only 2 digits
            'https://www.wsj.com/articles/test-1234',  # Only 4 digits (boundary)
            'https://www.wsj.com/nodash'  # No dash at all
        ]
        
        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertFalse(is_article(url), f"Should be invalid: {url}")
    
    def test_boundary_cases(self):
        """Test boundary cases for digit counting."""
        # Exactly 4 digits (boundary case)
        self.assertTrue(is_article('https://www.wsj.com/articles/test-article-1234'))
        
        # More than 4 digits
        self.assertTrue(is_article('https://www.wsj.com/articles/test-article-123456789'))
        
        # Mixed alphanumeric
        self.assertTrue(is_article('https://www.wsj.com/articles/test-article-abc12345'))


class TestExtractArticleLinks(unittest.TestCase):
    """Test extract_article_links function."""
    
    def test_extract_valid_links(self):
        """Test extraction of valid article links."""
        html = """
        <html>
        <body>
            <a href="https://www.wsj.com/articles/valid-article-12345678">Valid Article</a>
            <a href="https://www.wsj.com/business/another-valid-article-87654321">Another Valid</a>
            <a href="https://www.wsj.com/articles/with-query-params-11111111?mod=home">With Query Params</a>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        links = extract_article_links(soup)
        
        self.assertEqual(len(links), 3)
        self.assertIn('https://www.wsj.com/articles/valid-article-12345678', links)
        self.assertIn('https://www.wsj.com/business/another-valid-article-87654321', links)
        self.assertIn('https://www.wsj.com/articles/with-query-params-11111111', links)
    
    def test_filter_excluded_patterns(self):
        """Test filtering of excluded patterns."""
        html = """
        <html>
        <body>
            <a href="https://www.wsj.com/articles/valid-article-12345678">Valid Article</a>
            <a href="https://www.wsj.com/signin">Sign In</a>
            <a href="https://www.wsj.com/subscribe">Subscribe</a>
            <a href="https://www.wsj.com/video/test-video">Video</a>
            <a href="https://www.wsj.com/podcasts/test-podcast">Podcast</a>
            <a href="#fragment">Fragment</a>
            <a href="/relative/path">Relative Path</a>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        links = extract_article_links(soup)
        
        self.assertEqual(len(links), 1)
        self.assertIn('https://www.wsj.com/articles/valid-article-12345678', links)
    
    def test_empty_html(self):
        """Test extraction from empty HTML."""
        html = "<html><body></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        links = extract_article_links(soup)
        
        self.assertEqual(len(links), 0)
    
    def test_duplicate_links(self):
        """Test handling of duplicate links."""
        html = """
        <html>
        <body>
            <a href="https://www.wsj.com/articles/duplicate-article-12345678">Article 1</a>
            <a href="https://www.wsj.com/articles/duplicate-article-12345678">Article 1 Again</a>
            <a href="https://www.wsj.com/articles/unique-article-87654321">Article 2</a>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        links = extract_article_links(soup)
        
        self.assertEqual(len(links), 2)
        self.assertIn('https://www.wsj.com/articles/duplicate-article-12345678', links)
        self.assertIn('https://www.wsj.com/articles/unique-article-87654321', links)


class TestExtractArticleContent(unittest.TestCase):
    """Test extract_article_content function."""
    
    def test_complete_article_extraction(self):
        """Test extraction of complete article data."""
        html = """
        <html>
        <head>
            <meta name="description" content="This is a test article summary">
            <meta name="keywords" content="test, article, finance">
            <meta name="cXenseParse:recs:wsj-date" content="2024-01-01T12:00:00Z">
        </head>
        <body>
            <h1 data-testid="headline">Test Article Headline</h1>
            <div data-testid="article-content">
                <p>This is the first paragraph with sufficient content to be meaningful.</p>
                <p>This is the second paragraph with additional information and details.</p>
                <p>This is the third paragraph completing the article content.</p>
            </div>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        content_list = extract_article_content(soup)
        
        self.assertEqual(len(content_list), 1)
        content = content_list[0]
        self.assertEqual(content['headline'], 'Test Article Headline')
        self.assertEqual(content['summary'], 'This is a test article summary')
        self.assertEqual(content['keywords'], 'test, article, finance')
        self.assertEqual(content['date'], '2024-01-01')
        self.assertIn('first paragraph', content['content'])
        self.assertIn('second paragraph', content['content'])
        self.assertIn('third paragraph', content['content'])
    
    def test_minimal_article_extraction(self):
        """Test extraction from minimal HTML."""
        html = """
        <html>
        <body>
            <h1>Simple Headline</h1>
            <p>Simple content paragraph with enough text to be meaningful.</p>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        content_list = extract_article_content(soup)
        
        self.assertEqual(len(content_list), 1)
        content = content_list[0]
        self.assertEqual(content['headline'], 'Simple Headline')
        self.assertEqual(content['summary'], '')
        self.assertEqual(content['keywords'], '')
        self.assertEqual(content['date'], '')
        self.assertEqual(content['companies'], '')
    
    def test_stock_ticker_extraction(self):
        """Test extraction of stock ticker information."""
        html = """
        <html>
        <body>
            <h1>Stock Market News</h1>
            <div data-testid="article-content">
                <p>Apple Inc. stock information and market analysis.</p>
                <span style="display:unset">
                    <a data-type="company">Apple Inc.</a>
                    <a class="ChicletStyle">
                        AAPL
                        <span class="ChicletChange">+2.5%</span>
                        <span class="ArrowHiddenLabel">increase</span>
                    </a>
                </span>
            </div>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        content_list = extract_article_content(soup)
        
        self.assertEqual(len(content_list), 1)
        content = content_list[0]
        self.assertIn('Apple Inc.', content['companies'])
        self.assertIn('AAPL', content['companies'])
        self.assertIn('2.5%', content['companies'])
        self.assertIn('gain', content['companies'])
    
    def test_empty_content_handling(self):
        """Test handling of empty or insufficient content."""
        html = """
        <html>
        <body>
            <h1>Empty Article</h1>
            <p>Short</p>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        content_list = extract_article_content(soup)
        
        self.assertEqual(len(content_list), 1)
        content = content_list[0]
        self.assertEqual(content['headline'], 'Empty Article')
        self.assertEqual(content['content'], '')  # Too short to be included
    
    def test_newsletter_extraction(self):
        """Test extraction from newsletter format."""
        html = """
        <html>
        <body>
            <h1>Newsletter Section 1</h1>
            <td class="email-body__article">
                <p>First newsletter section with substantial content.</p>
            </td>
            <h1>Newsletter Section 2</h1>
            <td class="email-body__article">
                <p>Second newsletter section with more content.</p>
            </td>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        content_list = extract_article_content(soup)
        
        # Should extract multiple articles from newsletter
        self.assertGreaterEqual(len(content_list), 2)
        headlines = [article['headline'] for article in content_list]
        self.assertIn('Newsletter Section 1', headlines)
        self.assertIn('Newsletter Section 2', headlines)


class TestContentQualityCalculation(unittest.TestCase):
    """Test content quality calculation function."""
    
    def test_quality_calculation_basic(self):
        """Test basic quality calculation."""
        article = {
            'headline': 'Test Headline',
            'content': 'This is test content with sufficient length.',
            'summary': 'Test summary'
        }
        
        score = _calculate_content_quality([article])
        self.assertGreater(score, 0.0)
    
    def test_quality_calculation_comparison(self):
        """Test quality comparison between different articles."""
        short_article = {
            'headline': 'Short',
            'content': 'Short content.',
            'summary': 'Short summary'
        }
        
        long_article = {
            'headline': 'Long',
            'content': 'This is a much longer article with substantial content that should score higher.',
            'summary': 'Longer summary',
            'keywords': 'test, keywords',
            'date': '2024-01-01'
        }
        
        short_score = _calculate_content_quality([short_article])
        long_score = _calculate_content_quality([long_article])
        
        self.assertGreater(long_score, short_score)


class TestConstants(unittest.TestCase):
    """Test constants and configuration."""
    
    def test_topics_list(self):
        """Test that TOPICS list is properly defined."""
        self.assertIsInstance(TOPICS, list)
        self.assertGreater(len(TOPICS), 0)
        self.assertIn('', TOPICS)  # Main page
        self.assertIn('/business/', TOPICS)
        self.assertIn('/finance/', TOPICS)
    
    def test_exclude_patterns(self):
        """Test that EXCLUDE_PATTERNS is properly defined."""
        self.assertIsInstance(EXCLUDE_PATTERNS, list)
        self.assertGreater(len(EXCLUDE_PATTERNS), 0)
        self.assertIn('signin', EXCLUDE_PATTERNS)
        self.assertIn('login', EXCLUDE_PATTERNS)
        self.assertIn('subscri', EXCLUDE_PATTERNS)


class TestSafeGet(unittest.TestCase):
    """Test safe_get function."""
    
    @patch('wsj_adapter.wsj_adapter.time.sleep')
    def test_safe_get_with_timeout(self, mock_sleep):
        """Test safe_get with timeout parameter."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response
        
        result = safe_get('https://example.com', mock_session, timeout=30)
        
        self.assertEqual(result, mock_response)
        mock_session.get.assert_called_once_with('https://example.com', timeout=30)
        mock_sleep.assert_called_once()
    
    @patch('wsj_adapter.wsj_adapter.time.sleep')
    def test_safe_get_request_exception(self, mock_sleep):
        """Test safe_get with request exception."""
        mock_session = Mock()
        mock_session.get.side_effect = requests.RequestException("Network error")
        
        result = safe_get('https://example.com', mock_session)
        
        self.assertIsNone(result)
        mock_sleep.assert_called_once()
    
    @patch('wsj_adapter.wsj_adapter.time.sleep')
    def test_safe_get_http_error(self, mock_sleep):
        """Test safe_get with HTTP error."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_session.get.return_value = mock_response
        
        result = safe_get('https://example.com', mock_session)
        
        self.assertIsNone(result)
        mock_sleep.assert_called_once()


class TestCreateSession(unittest.TestCase):
    """Test create_session function."""
    
    def test_session_creation(self):
        """Test that create_session returns a properly configured session."""
        session = create_session()
        
        self.assertIsInstance(session, requests.Session)
        
        # Check that adapters are mounted
        https_adapter = session.get_adapter('https://example.com')
        http_adapter = session.get_adapter('http://example.com')
        
        self.assertIsNotNone(https_adapter)
        self.assertIsNotNone(http_adapter)
    
    def test_session_retry_configuration(self):
        """Test that session has retry configuration."""
        session = create_session()
        
        # Get the adapter and check it has retry configuration
        adapter = session.get_adapter('https://example.com')
        self.assertIsNotNone(adapter.max_retries)


if __name__ == '__main__':
    unittest.main() 