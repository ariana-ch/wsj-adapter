# WSJ Adapter

A Python package to download articles from the Wall Street Journal via the Wayback Machine.

## Description

The WSJ Adapter allows you to retrieve archived Wall Street Journal articles using the Internet Archive's Wayback Machine. This is particularly useful for researchers, analysts, and anyone who needs access to historical WSJ content for analysis or research purposes.

## Features

- **Multi-topic support**: Query different sections of WSJ (business, finance, politics, etc.)
- **Date range filtering**: Specify custom date ranges for your searches
- **Parallel processing**: Efficient concurrent downloading with configurable workers
- **Content extraction**: Clean extraction of headlines, content, summaries, and metadata
- **Stock ticker extraction**: Automatically extracts and formats stock information
- **Smart sampling**: Sample a configurable number of website captures per day
- **Sequential processing**: Process multiple article links until one returns a result
- **Newsletter support**: Extract content from WSJ newsletter formats
- **Rate limiting**: Built-in throttling to be respectful to the Wayback Machine

## Installation

### From your private repository

```bash
pip install wsj-adapter
```

### From source

```bash
git clone https://github.com/ariana-ch/wsj-adapter.git
cd wsj-adapter
pip install -e .
```

## Quick Start

```python
import datetime
from wsj_adapter import WSJAdapter

# Initialize the adapter
adapter = WSJAdapter(
    start_date=datetime.date(2024, 1, 1),
    end_date=datetime.date(2024, 1, 31),
    topics=['/business/', '/finance/'],  # Optional: specify topics
    max_workers=3,  # Optional: number of concurrent workers
    no_of_captures=10  # Optional: sample 10 captures per day per topic
)

# Download articles
articles = adapter.download()

# Process results
for article in articles:
    print(f"Headline: {article['headline']}")
    print(f"Date: {article['date']}")
    print(f"Summary: {article['summary']}")
    print(f"Content: {article['content'][:200]}...")
    print(f"Companies: {article['companies']}")
    print("-" * 50)
```

## Available Topics

The adapter supports the following WSJ topics:

- `''` - Main page
- `'/opinion/'` - Opinion section
- `'/business/'` - Business section
- `'/economy/'` - Economy section
- `'/finance/'` - Finance section
- `'/politics/'` - Politics section
- `'/us-news/'` - US News section
- `'/news/'` - General news
- `'/tech/'` - Technology section
- `'/world/'` - World news

## Article Data Structure

Each article returns a dictionary with the following fields:

```python
{
    'headline': str,      # Article headline
    'content': str,       # Full article content
    'summary': str,       # Article summary/description
    'keywords': str,      # Article keywords
    'companies': str,     # Stock ticker information
    'date': str,         # Publication date (YYYY-MM-DD)
    'url': str,          # Original article URL
    'timestamp': str,    # Wayback Machine timestamp
    'archive_url': str   # Full Wayback Machine URL
}
```

## Advanced Usage

### Custom Configuration

```python
from wsj_adapter import WSJAdapter, TOPICS

# Use all available topics
adapter = WSJAdapter(
    start_date=datetime.date(2024, 1, 1),
    end_date=datetime.date(2024, 1, 31),
    topics=TOPICS,  # Use all predefined topics
    max_workers=5,  # Increase workers for faster processing
    no_of_captures=15  # Sample 15 captures per day per topic
)
```

### Working with Large Date Ranges

```python
# For large date ranges, consider using fewer captures per day
adapter = WSJAdapter(
    start_date=datetime.date(2023, 1, 1),
    end_date=datetime.date(2023, 12, 31),
    no_of_captures=5,  # Sample fewer captures to reduce processing time
    max_workers=3  # Be conservative with workers for large ranges
)
```

### Accessing Raw Data

```python
# Get records and article links without downloading content
adapter = WSJAdapter(
    start_date=datetime.date(2024, 1, 1),
    end_date=datetime.date(2024, 1, 31)
)

# Get raw CDX records
records = adapter.get_all_records()
print(f"Found {len(records)} CDX records")

# Get article links
article_links = adapter.get_all_article_links(records)
print(f"Found {len(article_links)} article links")
```

## Rate Limiting and Ethics

This package includes built-in rate limiting to be respectful to the Wayback Machine:

- Random delays between requests (1-2 seconds)
- Automatic retries with exponential backoff
- Configurable timeout settings
- Connection pooling for efficiency

Please use this tool responsibly and in accordance with the Internet Archive's terms of service.

## Requirements

- Python 3.9+ (including Python 3.13)
- beautifulsoup4 (HTML/XML parsing)
- pandas (data manipulation)
- requests (HTTP client)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Support

For questions, bug reports, or feature requests, please open an issue on our [GitHub repository](https://github.com/ariana-ch/wsj-adapter/issues).

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a history of changes to this project. 