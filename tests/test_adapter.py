"""
Unit tests for WSJ Adapter.
"""

import unittest
import datetime
from unittest.mock import Mock, patch, MagicMock
import requests
from bs4 import BeautifulSoup

from wsj_adapter import WSJAdapter
from wsj_adapter.wsj_adapter import (
    safe_get, create_session, cdx_query, is_article, 
    extract_article_links, extract_article_content, 
    process_article_url, _calculate_content_quality
)


class TestWSJAdapterInit(unittest.TestCase):
    """Test WSJ Adapter initialization."""
    
    def test_init_with_default_parameters(self):
        """Test adapter initialization with default parameters."""
        adapter = WSJAdapter(
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 1, 31)
        )
        
        self.assertEqual(adapter.start_date, datetime.date(2024, 1, 1))
        self.assertEqual(adapter.end_date, datetime.date(2024, 1, 31))
        self.assertEqual(adapter.url, 'www.wsj.com')
        self.assertEqual(adapter.max_workers, 3)
        self.assertEqual(adapter.no_of_captures, 10)
        self.assertIsNotNone(adapter.session)
    
    def test_init_with_custom_parameters(self):
        """Test adapter initialization with custom parameters."""
        custom_topics = ['/business/', '/finance/']
        
        adapter = WSJAdapter(
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 1, 31),
            topics=custom_topics,
            max_workers=5,
            no_of_captures=15
        )
        
        self.assertEqual(adapter.topics, custom_topics)
        self.assertEqual(adapter.max_workers, 5)
        self.assertEqual(adapter.no_of_captures, 15)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""
    
    def test_create_session(self):
        """Test session creation."""
        session = create_session()
        
        self.assertIsInstance(session, requests.Session)
        self.assertIsNotNone(session.get_adapter('https://'))
        self.assertIsNotNone(session.get_adapter('http://'))
    
    @patch('wsj_adapter.wsj_adapter.time.sleep')
    @patch('requests.Session.get')
    def test_safe_get_success(self, mock_get, mock_sleep):
        """Test successful safe_get request."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        session = Mock()
        session.get.return_value = mock_response
        
        result = safe_get('https://example.com', session)
        
        self.assertEqual(result, mock_response)
        mock_sleep.assert_called_once()
    
    @patch('wsj_adapter.wsj_adapter.time.sleep')
    @patch('requests.Session.get')
    def test_safe_get_failure(self, mock_get, mock_sleep):
        """Test failed safe_get request."""
        mock_get.side_effect = requests.RequestException("Connection error")
        
        session = Mock()
        session.get.side_effect = requests.RequestException("Connection error")
        
        result = safe_get('https://example.com', session)
        
        self.assertIsNone(result)
    
    def test_is_article_valid(self):
        """Test is_article function with valid URLs."""
        valid_urls = [
            'https://www.wsj.com/articles/test-article-12345678',
            'https://www.wsj.com/articles/another-test-article-987654321',
            'https://www.wsj.com/business/test-business-article-11111111'
        ]
        
        for url in valid_urls:
            with self.subTest(url=url):
                self.assertTrue(is_article(url))
    
    def test_is_article_invalid(self):
        """Test is_article function with invalid URLs."""
        invalid_urls = [
            'https://www.wsj.com/articles/test-article-123',  # Too few digits
            'https://www.wsj.com/articles/test-article',       # No digits
            'https://www.wsj.com/articles/no-dash-url',        # No dash
            'https://www.wsj.com/about'                        # Not an article
        ]
        
        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertFalse(is_article(url))
    
    def test_extract_article_links(self):
        """Test article link extraction from HTML."""
        html = """
        <html>
        <body>
            <a href="https://www.wsj.com/articles/test-article-12345678">Test Article</a>
            <a href="https://www.wsj.com/articles/another-article-87654321">Another Article</a>
            <a href="https://www.wsj.com/signin">Sign In</a>
            <a href="#fragment">Fragment Link</a>
            <a href="/about">About</a>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        links = extract_article_links(soup)
        
        self.assertEqual(len(links), 2)
        self.assertIn('https://www.wsj.com/articles/test-article-12345678', links)
        self.assertIn('https://www.wsj.com/articles/another-article-87654321', links)
    
    def test_extract_article_content_single_article(self):
        """Test article content extraction for single article."""
        html = """
        <html>
        <head>
            <meta name="description" content="Test article summary">
            <meta name="keywords" content="test, article, keywords">
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
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        content_list = extract_article_content(soup)
        
        self.assertEqual(len(content_list), 1)
        content = content_list[0]
        self.assertEqual(content['headline'], 'Test Article Headline')
        self.assertEqual(content['summary'], 'Test article summary')
        self.assertEqual(content['keywords'], 'test, article, keywords')
        self.assertEqual(content['date'], '2024-01-01')
        self.assertIn('first paragraph', content['content'])
        self.assertIn('second paragraph', content['content'])
    
    def test_extract_article_content_newsletter(self):
        """Test article content extraction for newsletter format."""
        html = """
        <html>
        <body>
            <h1>Newsletter Section 1</h1>
            <td class="email-body__article">
                <p>This is the first newsletter section with substantial content.</p>
            </td>
            <h1>Newsletter Section 2</h1>
            <td class="email-body__article">
                <p>This is the second newsletter section with more content.</p>
            </td>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        content_list = extract_article_content(soup)
        
        self.assertGreaterEqual(len(content_list), 2)
        # Should select newsletter extraction due to multiple articles
        self.assertIn('Newsletter Section 1', [article['headline'] for article in content_list])
        self.assertIn('Newsletter Section 2', [article['headline'] for article in content_list])
    
    def test_extract_article_content_method_selection(self):
        """Test that the correct extraction method is selected."""
        # Test single article (should prefer single article extraction)
        single_article_html = """
        <html>
        <head>
            <meta name="description" content="Comprehensive article summary">
            <meta name="keywords" content="finance, markets, stocks">
            <meta name="cXenseParse:recs:wsj-date" content="2024-01-01">
        </head>
        <body>
            <h1 data-testid="headline">Comprehensive Financial Article</h1>
            <div data-testid="article-content">
                <p>This is a very comprehensive article with substantial content that should score higher than newsletter extraction.</p>
                <p>It contains multiple paragraphs with detailed information about financial markets and economic analysis.</p>
                <p>The content is structured and includes proper metadata which should give it a high quality score.</p>
            </div>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(single_article_html, 'html.parser')
        content_list = extract_article_content(soup)
        
        # Should select single article extraction for comprehensive content
        self.assertEqual(len(content_list), 1)
        self.assertIn('Comprehensive Financial Article', content_list[0]['headline'])


class TestContentQualityCalculation(unittest.TestCase):
    """Test content quality calculation function."""
    
    def test_calculate_content_quality_empty_list(self):
        """Test quality calculation with empty list."""
        score = _calculate_content_quality([])
        self.assertEqual(score, 0.0)
    
    def test_calculate_content_quality_single_article(self):
        """Test quality calculation with single article."""
        article = {
            'headline': 'Test Headline',
            'content': 'This is a test article with substantial content that should score well.',
            'summary': 'Test summary',
            'keywords': 'test, article',
            'companies': 'Test Company',
            'date': '2024-01-01'
        }
        
        score = _calculate_content_quality([article])
        
        # Should have base content score + bonuses for all fields
        self.assertGreater(score, 0.0)
        self.assertGreater(score, 50.0)  # Should be substantial with all bonuses
    
    def test_calculate_content_quality_multiple_articles(self):
        """Test quality calculation with multiple articles."""
        articles = [
            {
                'headline': 'Article 1',
                'content': 'First article content with good length.',
                'summary': 'Summary 1',
                'keywords': 'test',
                'date': '2024-01-01'
            },
            {
                'headline': 'Article 2',
                'content': 'Second article content with good length.',
                'summary': 'Summary 2',
                'keywords': 'test',
                'date': '2024-01-01'
            }
        ]
        
        score = _calculate_content_quality(articles)
        
        # Should be average of both articles
        self.assertGreater(score, 0.0)
        self.assertGreater(score, 50.0)
    
    def test_calculate_content_quality_short_content_penalty(self):
        """Test that very short content gets penalized."""
        short_article = {
            'headline': 'Short Article',
            'content': 'Very short content.',
            'summary': 'Short summary'
        }
        
        long_article = {
            'headline': 'Long Article',
            'content': 'This is a much longer article with substantial content that should score significantly higher than the short article.',
            'summary': 'Longer summary'
        }
        
        short_score = _calculate_content_quality([short_article])
        long_score = _calculate_content_quality([long_article])
        
        # Long article should score higher
        self.assertGreater(long_score, short_score)
    
    def test_calculate_content_quality_missing_fields(self):
        """Test quality calculation with missing optional fields."""
        minimal_article = {
            'headline': 'Minimal Article',
            'content': 'Basic content without optional fields.'
        }
        
        complete_article = {
            'headline': 'Complete Article',
            'content': 'Complete content with all fields.',
            'summary': 'Summary',
            'keywords': 'keywords',
            'companies': 'companies',
            'date': '2024-01-01'
        }
        
        minimal_score = _calculate_content_quality([minimal_article])
        complete_score = _calculate_content_quality([complete_article])
        
        # Complete article should score higher
        self.assertGreater(complete_score, minimal_score)


class TestWSJAdapterMethods(unittest.TestCase):
    """Test WSJ Adapter methods."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.adapter = WSJAdapter(
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 1, 31)
        )
    
    @patch('wsj_adapter.wsj_adapter.cdx_query')
    def test_get_all_records(self, mock_cdx_query):
        """Test get_all_records method."""
        mock_records = [
            ['20240101120000', 'www.wsj.com/business/'],
            ['20240102120000', 'www.wsj.com/finance/']
        ]
        mock_cdx_query.return_value = mock_records
        
        records = self.adapter.get_all_records()
        
        self.assertEqual(len(records), len(mock_records) * len(self.adapter.topics))
        self.assertEqual(mock_cdx_query.call_count, len(self.adapter.topics))
    
    @patch('wsj_adapter.wsj_adapter.safe_get')
    def test_get_all_article_links(self, mock_safe_get):
        """Test get_all_article_links method."""
        # Mock response
        mock_response = Mock()
        mock_response.text = """
        <html>
        <body>
            <a href="https://www.wsj.com/articles/test-article-12345678">Test Article</a>
        </body>
        </html>
        """
        mock_safe_get.return_value = mock_response
        
        records = [['20240101120000', 'www.wsj.com/business/']]
        links = self.adapter.get_all_article_links(records)
        
        self.assertIsInstance(links, list)
        mock_safe_get.assert_called()
    
    @patch('wsj_adapter.wsj_adapter.ThreadPoolExecutor')
    @patch('wsj_adapter.wsj_adapter.process_article_url')
    def test_download(self, mock_process_article_url, mock_executor):
        """Test download method."""
        # Mock the ThreadPoolExecutor
        mock_future = Mock()
        mock_future.result.return_value = [{
            'headline': 'Test Article',
            'content': 'Test content',
            'url': 'https://www.wsj.com/articles/test-12345678'
        }]
        
        mock_executor_instance = Mock()
        mock_executor_instance.submit.return_value = mock_future
        mock_executor_instance.__enter__.return_value = mock_executor_instance
        mock_executor_instance.__exit__.return_value = None
        mock_executor.return_value = mock_executor_instance
        
        # Mock the adapter methods
        with patch.object(self.adapter, 'get_all_records') as mock_get_records:
            with patch.object(self.adapter, 'get_all_article_links') as mock_get_links:
                mock_get_records.return_value = [['20240101120000', 'www.wsj.com/business/']]
                mock_get_links.return_value = ['https://www.wsj.com/articles/test-12345678']
                
                articles = self.adapter.download()
                
                self.assertIsInstance(articles, list)
                mock_get_records.assert_called_once()
                mock_get_links.assert_called_once()


class TestCDXQuery(unittest.TestCase):
    """Test CDX query function."""
    
    @patch('wsj_adapter.wsj_adapter.safe_get')
    def test_cdx_query_success(self, mock_safe_get):
        """Test successful CDX query."""
        mock_response = Mock()
        mock_response.json.return_value = [
            ['timestamp', 'original'],  # header
            ['20240101120000', 'www.wsj.com/business/'],
            ['20240102120000', 'www.wsj.com/finance/']
        ]
        mock_safe_get.return_value = mock_response
        
        session = Mock()
        records = cdx_query(
            'www.wsj.com/business/',
            session,
            datetime.date(2024, 1, 1),
            datetime.date(2024, 1, 31)
        )
        
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0], ['20240101120000', 'www.wsj.com/business/'])
        self.assertEqual(records[1], ['20240102120000', 'www.wsj.com/finance/'])
    
    @patch('wsj_adapter.wsj_adapter.safe_get')
    def test_cdx_query_failure(self, mock_safe_get):
        """Test failed CDX query."""
        mock_safe_get.return_value = None
        
        session = Mock()
        
        with self.assertRaises(AttributeError):
            cdx_query(
                'www.wsj.com/business/',
                session,
                datetime.date(2024, 1, 1),
                datetime.date(2024, 1, 31)
            )


class TestProcessArticleURL(unittest.TestCase):
    """Test process_article_url function."""
    
    @patch('wsj_adapter.wsj_adapter.safe_get')
    def test_process_article_url_success(self, mock_safe_get):
        """Test successful article URL processing."""
        mock_response = Mock()
        mock_response.text = """
        <html>
        <head>
            <meta name="description" content="Test article summary">
        </head>
        <body>
            <h1 data-testid="headline">Test Article Headline</h1>
            <div data-testid="article-content">
                <p>This is a test article with sufficient content to be processed.</p>
            </div>
        </body>
        </html>
        """
        mock_safe_get.return_value = mock_response
        
        session = Mock()
        url = 'https://web.archive.org/web/20240101120000/https://www.wsj.com/articles/test-12345678'
        
        result = process_article_url(url, session)
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)  # Should return a list with one article
        article = result[0]
        self.assertEqual(article['headline'], 'Test Article Headline')
        self.assertEqual(article['timestamp'], '20240101120000')
        self.assertEqual(article['archive_url'], url)
    
    @patch('wsj_adapter.wsj_adapter.safe_get')
    def test_process_article_url_failure(self, mock_safe_get):
        """Test failed article URL processing."""
        mock_safe_get.return_value = None
        
        session = Mock()
        url = 'https://web.archive.org/web/20240101120000/https://www.wsj.com/articles/test-12345678'
        
        result = process_article_url(url, session)
        
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main() 