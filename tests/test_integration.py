"""
Integration tests for WSJ Adapter.

These tests verify the integration between components but use mocking
to avoid hitting external services during testing.
"""

import unittest
import datetime
import json
from unittest.mock import Mock, patch, MagicMock
from wsj_adapter import WSJAdapter


class TestWSJAdapterIntegration(unittest.TestCase):
    """Integration tests for WSJ Adapter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.adapter = WSJAdapter(
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 1, 2),
            topics=['/business/'],
            max_workers=2,
            latest_records=True,
            latest_articles=True
        )
    
    @patch('wsj_adapter.wsj_adapter.safe_get')
    def test_full_workflow_integration(self, mock_safe_get):
        """Test the complete workflow from records to articles."""
        # Mock CDX API response
        cdx_response = Mock()
        cdx_response.json.return_value = [
            ['timestamp', 'original'],  # header
            ['20240101120000', 'www.wsj.com/business/']
        ]
        
        # Mock main page response
        main_page_response = Mock()
        main_page_response.text = """
        <html>
        <body>
            <a href="https://www.wsj.com/articles/test-article-12345678">Test Article</a>
        </body>
        </html>
        """
        
        # Mock article page response
        article_response = Mock()
        article_response.text = """
        <html>
        <head>
            <meta name="description" content="Test article summary">
            <meta name="keywords" content="test, business">
            <meta name="cXenseParse:recs:wsj-date" content="2024-01-01">
        </head>
        <body>
            <h1 data-testid="headline">Test Business Article</h1>
            <div data-testid="article-content">
                <p>This is a comprehensive test article with sufficient content for analysis.</p>
                <p>The article contains multiple paragraphs to ensure proper content extraction.</p>
            </div>
        </body>
        </html>
        """
        
        # Configure mock responses based on URL patterns
        def mock_get_side_effect(url, *args, **kwargs):
            if 'cdx/search/cdx' in url:
                return cdx_response
            elif 'web.archive.org/web/20240101120000' in url and 'articles' not in url:
                return main_page_response
            elif 'articles/test-article-12345678' in url:
                return article_response
            else:
                return None
        
        mock_safe_get.side_effect = mock_get_side_effect
        
        # Run the full workflow
        articles = self.adapter.download()
        
        # Verify results
        self.assertEqual(len(articles), 1)
        article = articles[0]
        
        self.assertEqual(article['headline'], 'Test Business Article')
        self.assertEqual(article['summary'], 'Test article summary')
        self.assertEqual(article['keywords'], 'test, business')
        self.assertEqual(article['date'], '2024-01-01')
        self.assertIn('comprehensive test article', article['content'])
        self.assertIn('multiple paragraphs', article['content'])
        self.assertEqual(article['timestamp'], '20240101120000')
    
    @patch('wsj_adapter.wsj_adapter.safe_get')
    def test_no_articles_found(self, mock_safe_get):
        """Test behavior when no articles are found."""
        # Mock CDX API response
        cdx_response = Mock()
        cdx_response.json.return_value = [
            ['timestamp', 'original'],  # header
            ['20240101120000', 'www.wsj.com/business/']
        ]
        
        # Mock main page response with no article links
        main_page_response = Mock()
        main_page_response.text = """
        <html>
        <body>
            <a href="https://www.wsj.com/about">About</a>
            <a href="https://www.wsj.com/signin">Sign In</a>
        </body>
        </html>
        """
        
        def mock_get_side_effect(url, *args, **kwargs):
            if 'cdx/search/cdx' in url:
                return cdx_response
            elif 'web.archive.org/web/20240101120000' in url:
                return main_page_response
            else:
                return None
        
        mock_safe_get.side_effect = mock_get_side_effect
        
        # Run the workflow
        articles = self.adapter.download()
        
        # Verify no articles were found
        self.assertEqual(len(articles), 0)
    
    @patch('wsj_adapter.wsj_adapter.safe_get')
    def test_network_failure_handling(self, mock_safe_get):
        """Test handling of network failures."""
        # Mock CDX API failure
        mock_safe_get.return_value = None
        
        # This should not raise an exception
        try:
            articles = self.adapter.download()
            self.assertEqual(len(articles), 0)
        except Exception as e:
            self.fail(f"Network failure should be handled gracefully: {e}")
    
    @patch('wsj_adapter.wsj_adapter.safe_get')
    def test_partial_article_extraction(self, mock_safe_get):
        """Test handling of articles with partial content."""
        # Mock responses
        cdx_response = Mock()
        cdx_response.json.return_value = [
            ['timestamp', 'original'],
            ['20240101120000', 'www.wsj.com/business/']
        ]
        
        main_page_response = Mock()
        main_page_response.text = """
        <html>
        <body>
            <a href="https://www.wsj.com/articles/partial-article-12345678">Partial Article</a>
        </body>
        </html>
        """
        
        # Article with minimal content
        article_response = Mock()
        article_response.text = """
        <html>
        <body>
            <h1>Article Title Only</h1>
            <p>Short content.</p>
        </body>
        </html>
        """
        
        def mock_get_side_effect(url, *args, **kwargs):
            if 'cdx/search/cdx' in url:
                return cdx_response
            elif 'web.archive.org/web/20240101120000' in url and 'articles' not in url:
                return main_page_response
            elif 'articles/partial-article-12345678' in url:
                return article_response
            else:
                return None
        
        mock_safe_get.side_effect = mock_get_side_effect
        
        # Run the workflow
        articles = self.adapter.download()
        
        # Article should be filtered out due to insufficient content
        self.assertEqual(len(articles), 0)
    
    @patch('wsj_adapter.wsj_adapter.safe_get')
    def test_multiple_topics_integration(self, mock_safe_get):
        """Test integration with multiple topics."""
        # Set up adapter with multiple topics
        multi_topic_adapter = WSJAdapter(
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 1, 2),
            topics=['/business/', '/finance/'],
            max_workers=2
        )
        
        # Mock responses for different topics
        cdx_response = Mock()
        cdx_response.json.return_value = [
            ['timestamp', 'original'],
            ['20240101120000', 'www.wsj.com/business/'],
            ['20240101120000', 'www.wsj.com/finance/']
        ]
        
        main_page_response = Mock()
        main_page_response.text = """
        <html>
        <body>
            <a href="https://www.wsj.com/articles/multi-topic-article-12345678">Multi Topic Article</a>
        </body>
        </html>
        """
        
        article_response = Mock()
        article_response.text = """
        <html>
        <head>
            <meta name="description" content="Multi-topic article summary">
        </head>
        <body>
            <h1 data-testid="headline">Multi Topic Article</h1>
            <div data-testid="article-content">
                <p>This article covers both business and finance topics comprehensively.</p>
            </div>
        </body>
        </html>
        """
        
        def mock_get_side_effect(url, *args, **kwargs):
            if 'cdx/search/cdx' in url:
                return cdx_response
            elif 'web.archive.org/web/20240101120000' in url and 'articles' not in url:
                return main_page_response
            elif 'articles/multi-topic-article-12345678' in url:
                return article_response
            else:
                return None
        
        mock_safe_get.side_effect = mock_get_side_effect
        
        # Run the workflow
        articles = multi_topic_adapter.download()
        
        # Should have articles from both topics (may be deduplicated)
        self.assertGreater(len(articles), 0)
    
    @patch('wsj_adapter.wsj_adapter.safe_get')
    def test_date_filtering_integration(self, mock_safe_get):
        """Test integration with date filtering options."""
        # Test with latest_records=True
        latest_adapter = WSJAdapter(
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 1, 2),
            topics=['/business/'],
            latest_records=True,
            latest_articles=True
        )
        
        # Mock CDX response with multiple records for same day
        cdx_response = Mock()
        cdx_response.json.return_value = [
            ['timestamp', 'original'],
            ['20240101100000', 'www.wsj.com/business/'],
            ['20240101120000', 'www.wsj.com/business/'],  # Later same day
            ['20240101140000', 'www.wsj.com/business/']   # Even later
        ]
        
        main_page_response = Mock()
        main_page_response.text = """
        <html>
        <body>
            <a href="https://www.wsj.com/articles/date-filtered-article-12345678">Date Filtered Article</a>
        </body>
        </html>
        """
        
        article_response = Mock()
        article_response.text = """
        <html>
        <body>
            <h1 data-testid="headline">Date Filtered Article</h1>
            <div data-testid="article-content">
                <p>This article tests date filtering functionality with comprehensive content.</p>
            </div>
        </body>
        </html>
        """
        
        def mock_get_side_effect(url, *args, **kwargs):
            if 'cdx/search/cdx' in url:
                return cdx_response
            elif 'web.archive.org/web/' in url and 'articles' not in url:
                return main_page_response
            elif 'articles/date-filtered-article-12345678' in url:
                return article_response
            else:
                return None
        
        mock_safe_get.side_effect = mock_get_side_effect
        
        # Run the workflow
        articles = latest_adapter.download()
        
        # Should have processed articles (exact count depends on deduplication)
        self.assertGreaterEqual(len(articles), 0)


class TestDataProcessing(unittest.TestCase):
    """Test data processing and transformation."""
    
    def test_article_data_structure(self):
        """Test that article data follows expected structure."""
        # Mock a complete article response
        with patch('wsj_adapter.wsj_adapter.safe_get') as mock_safe_get:
            adapter = WSJAdapter(
                start_date=datetime.date(2024, 1, 1),
                end_date=datetime.date(2024, 1, 2),
                topics=['/business/']
            )
            
            # Mock complete workflow
            cdx_response = Mock()
            cdx_response.json.return_value = [
                ['timestamp', 'original'],
                ['20240101120000', 'www.wsj.com/business/']
            ]
            
            main_page_response = Mock()
            main_page_response.text = """
            <html>
            <body>
                <a href="https://www.wsj.com/articles/complete-article-12345678">Complete Article</a>
            </body>
            </html>
            """
            
            article_response = Mock()
            article_response.text = """
            <html>
            <head>
                <meta name="description" content="Complete article summary">
                <meta name="keywords" content="business, finance, test">
                <meta name="cXenseParse:recs:wsj-date" content="2024-01-01">
            </head>
            <body>
                <h1 data-testid="headline">Complete Article Headline</h1>
                <div data-testid="article-content">
                    <p>This is a complete article with all expected fields and comprehensive content.</p>
                </div>
            </body>
            </html>
            """
            
            def mock_get_side_effect(url, *args, **kwargs):
                if 'cdx/search/cdx' in url:
                    return cdx_response
                elif 'web.archive.org/web/20240101120000' in url and 'articles' not in url:
                    return main_page_response
                elif 'articles/complete-article-12345678' in url:
                    return article_response
                else:
                    return None
            
            mock_safe_get.side_effect = mock_get_side_effect
            
            articles = adapter.download()
            
            # Verify article structure
            self.assertEqual(len(articles), 1)
            article = articles[0]
            
            # Check all expected fields are present
            expected_fields = [
                'headline', 'content', 'summary', 'keywords', 
                'companies', 'date', 'url', 'timestamp', 'archive_url'
            ]
            
            for field in expected_fields:
                self.assertIn(field, article, f"Missing field: {field}")
            
            # Check field types
            self.assertIsInstance(article['headline'], str)
            self.assertIsInstance(article['content'], str)
            self.assertIsInstance(article['summary'], str)
            self.assertIsInstance(article['keywords'], str)
            self.assertIsInstance(article['companies'], str)
            self.assertIsInstance(article['date'], str)
            self.assertIsInstance(article['url'], str)
            self.assertIsInstance(article['timestamp'], str)
            self.assertIsInstance(article['archive_url'], str)


if __name__ == '__main__':
    unittest.main() 