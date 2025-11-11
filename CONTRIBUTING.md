# Contributing to Wikipedia Terminal

Thank you for your interest in contributing! 🎉

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/rafaelchandane/wikipedia-terminal/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Python version, OS, ZIM file details
   - Error messages/logs if applicable

### Suggesting Features

1. Check existing [Issues](https://github.com/rafaelchandane/wikipedia-terminal/issues)
2. Create a new issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Potential implementation approach (if known)

### Submitting Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Write/update tests (when test suite exists)
5. Update documentation if needed
6. Commit with clear messages (`git commit -m 'Add amazing feature'`)
7. Push to your fork (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings (Google style)
- Keep functions focused and small
- Add comments for complex logic

### Development Setup

```bash
git clone https://github.com/rafaelchandane/wikipedia-terminal.git
cd wikipedia-terminal
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

### Testing

```bash
# Run tests (coming soon)
pytest

# With coverage
pytest --cov=src
```

## Code of Conduct

Be respectful, inclusive, and professional. We want this to be a welcoming community for everyone.

## Questions?

Feel free to ask in [Discussions](https://github.com/rafaelchandane/wikipedia-terminal/discussions) or open an issue!
