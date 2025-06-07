# Contributing to ProRef

Thank you for your interest in contributing to ProRef! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How to Contribute

1. Fork the repository
2. Create a new branch for your feature or bugfix
3. Make your changes
4. Write or update tests as needed
5. Ensure all tests pass
6. Submit a pull request

## Development Setup

1. Clone your fork:
   ```bash
   git clone https://github.com/your-username/proref.git
   cd proref
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   ```

3. Install dependencies:
   ```bash
   pip install -e .
   ```

4. Copy `.env.example` to `.env` and fill in your configuration:
   ```bash
   cp .env.example .env
   ```

## Pull Request Process

1. Update the README.md with details of changes if needed
2. Update the documentation if you're changing functionality
3. The PR will be merged once you have the sign-off of at least one maintainer

## Style Guide

- Follow PEP 8 style guide for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions small and focused
- Write docstrings for all public functions and classes

## Testing

- Write tests for new features
- Ensure all tests pass before submitting a PR
- Update tests if you're changing existing functionality

## Documentation

- Update documentation for any new features or changes
- Keep the README.md up to date
- Add comments to complex code sections

## Questions?

Feel free to open an issue if you have any questions about contributing. 