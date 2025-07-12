# Contributing to WSJ Adapter

First off, thank you for considering contributing to WSJ Adapter! It's people like you that make this project a great tool for the community.

## Code of Conduct

This project and everyone participating in it is governed by our commitment to creating a welcoming and inclusive environment. Please be respectful and constructive in all interactions.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** with code snippets
- **Describe the behavior you observed** and what you expected
- **Include your environment details** (Python version, OS, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title**
- **Provide a step-by-step description** of the suggested enhancement
- **Provide specific examples** to demonstrate the enhancement
- **Describe the current behavior** and explain the desired behavior
- **Explain why this enhancement would be useful**

### Pull Requests

1. Fork the repository
2. Create a new branch for your feature (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add some amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ariana-ch/wsj-adapter.git
   cd wsj-adapter
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Run tests:
   ```bash
   pytest
   ```

## Style Guide

### Python Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write descriptive docstrings for all functions and classes
- Keep lines under 100 characters where possible

### Testing

- Write unit tests for new functionality
- Ensure all tests pass before submitting a PR
- Aim for good test coverage
- Use meaningful test names that describe what is being tested

### Documentation

- Update README.md if you change functionality
- Add docstrings to new functions and classes
- Update CHANGELOG.md with your changes
- Include examples in docstrings where helpful

## Code Review Process

1. All submissions require review before merging
2. We may ask for changes or improvements
3. Once approved, maintainers will merge your PR
4. We aim to respond to PRs within a few days

## Development Guidelines

### Adding New Features

- Create an issue first to discuss the feature
- Ensure the feature aligns with the project's goals
- Add comprehensive tests
- Update documentation

### Bug Fixes

- Include a test that reproduces the bug
- Fix the bug with minimal code changes
- Ensure the fix doesn't break existing functionality

### Performance Improvements

- Include benchmarks showing the improvement
- Ensure the change doesn't negatively impact other areas
- Document any trade-offs

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=wsj_adapter

# Run specific test file
pytest tests/test_adapter.py

# Run specific test
pytest tests/test_adapter.py::test_wsj_adapter_init
```

### Writing Tests

- Place tests in the `tests/` directory
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies (like HTTP requests)

## Documentation

### Building Documentation

If you're updating documentation:

1. Install documentation dependencies
2. Make your changes to the relevant markdown files
3. Test that links work correctly
4. Update the table of contents if needed

## Release Process

(For maintainers)

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create a git tag
4. Push to repository
5. Create a GitHub release

## Questions?

If you have questions about contributing, please:

1. Check the existing issues and documentation
2. Create a new issue with your question
3. Reach out to the maintainers

Thank you for contributing to WSJ Adapter! 🎉 