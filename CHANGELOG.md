# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of WSJ Adapter package
- WSJAdapter class for downloading WSJ articles via Wayback Machine
- Support for multiple WSJ topics (business, finance, politics, etc.)
- Parallel processing with configurable workers
- Rate limiting and retry mechanisms
- Content extraction with metadata parsing
- Stock ticker information extraction
- Flexible date range filtering
- Options for latest records/articles per day
- Comprehensive documentation and examples
- Full test suite with unit and integration tests
- Multiple installation options and requirements files
- Python 3.13 support
- Enhanced development tooling (mypy, black, pytest-cov, etc.)

### Changed
- **BREAKING**: Replaced `bs4>=0.0.2` with `beautifulsoup4>=4.12.0` for direct dependency management
- Updated minimum pandas version from 1.3.0 to 1.5.0 for performance improvements
- Updated minimum requests version from 2.32.0 to 2.28.0 for better compatibility
- Enhanced development dependencies with comprehensive tooling
- Improved package metadata and classifiers
- Added support for Python 3.13
- Enhanced documentation with dependency analysis

### Fixed
- Fixed invalid regex escape sequence warning in date parsing
- Resolved dependency confusion with bs4 dummy package
- Improved error handling in content extraction

### Security
- Updated to secure dependency versions with latest security patches
- Implemented proper version constraints for security updates
- Added security considerations documentation

## [0.0.1] - 2024-01-01

### Added
- Initial version of WSJ Adapter
- Basic article extraction functionality
- Wayback Machine integration
- Multi-threading support
- Content parsing and cleaning
- Stock ticker extraction
- Comprehensive logging
- Error handling and retries 