# WSJ Adapter Examples

This directory contains example scripts demonstrating how to use the WSJ Adapter package.

## Available Examples

### 1. Basic Usage (`basic_usage.py`)

A simple example showing the fundamental functionality of the WSJ Adapter.

**Features demonstrated:**
- Basic adapter initialization
- Simple article downloading
- Basic result processing and display

**Usage:**
```bash
python basic_usage.py
```

### 2. Advanced Usage (`advanced_usage.py`)

A comprehensive example showcasing advanced features and configurations.

**Features demonstrated:**
- Custom topic selection
- Working with raw CDX records
- Different configuration options
- Article analysis and statistics
- Result saving to JSON files

**Usage:**
```bash
python advanced_usage.py
```

### 3. Data Analysis (`data_analysis.py`)

An example focused on analyzing and processing downloaded articles.

**Features demonstrated:**
- Content analysis and keyword extraction
- Company mention tracking
- Statistical analysis of articles
- DataFrame creation with pandas
- Data export to CSV and JSON

**Usage:**
```bash
python data_analysis.py
```

## Prerequisites

Make sure you have the WSJ Adapter package installed:

```bash
pip install wsj-adapter
```

Or if you're working with the development version:

```bash
pip install -e .
```

## Customization

Each example can be easily customized by modifying the parameters:

### Date Ranges
```python
# Modify these lines in any example
start_date=datetime.date(2024, 1, 1),
end_date=datetime.date(2024, 1, 31),
```

### Topics
```python
# Use specific topics
topics=['/business/', '/finance/', '/tech/'],

# Or use all available topics
from wsj_adapter import TOPICS
topics=TOPICS,
```

### Performance Settings
```python
# Adjust workers and filtering
max_workers=5,          # More workers for faster processing
latest_records=True,    # Get only latest record per day
latest_articles=True,   # Get only latest article per day
```

## Output Files

The examples may create output files in your current directory:

- `wsj_articles.json` - Raw article data from basic usage
- `advanced_example_results.json` - Results from advanced example
- `analysis_results.json` - Raw data from data analysis
- `analysis_results.csv` - Processed data in CSV format

## Rate Limiting

All examples include built-in rate limiting to be respectful to the Wayback Machine. If you need to process larger datasets:

1. Use `latest_records=True` and `latest_articles=True` to reduce duplicates
2. Keep `max_workers` low (2-5) for large date ranges
3. Process data in smaller chunks for very large datasets

## Error Handling

The examples include comprehensive error handling, but if you encounter issues:

1. **Network errors**: The adapter automatically retries failed requests
2. **No articles found**: Check your date range and topics
3. **Rate limiting**: Reduce `max_workers` or add delays between runs

## Extending the Examples

You can extend these examples by:

1. **Adding new analysis functions** to `data_analysis.py`
2. **Creating custom filters** for specific types of articles
3. **Adding new output formats** (XML, Excel, etc.)
4. **Implementing caching** to avoid re-downloading articles
5. **Adding email notifications** for completed downloads

## Example Output

Here's what you might see when running the basic example:

```
WSJ Adapter - Basic Usage Example
========================================
Configured adapter for date range: 2024-01-01 to 2024-01-02
Topics: ['/business/', '/finance/']
Max workers: 2

Starting download...
Successfully downloaded 5 articles

Article 1:
  Headline: Stock Market Rebounds After Fed Decision
  Date: 2024-01-01
  Summary: Markets showed strong gains following the Federal Reserve's latest policy announcement...
  Companies: Apple Inc. AAPL (+2.3% gain), Microsoft Corp. MSFT (+1.8% gain)
  URL: https://www.wsj.com/articles/stock-market-rebounds-12345678

... and 2 more articles
Basic usage example completed!
```

## Getting Help

If you need help with the examples:

1. Check the main [README.md](../README.md) for general usage
2. Look at the [API documentation](../src/wsj_adapter/wsj_adapter.py) for detailed function information
3. Create an issue on the [GitHub repository](https://github.com/ariana-ch/wsj-adapter/issues)

## Contributing

If you create useful examples or improvements, please consider contributing them back to the project! 