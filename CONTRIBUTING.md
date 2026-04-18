# Contributing to Kloud Kompass

Thank you for your interest in contributing to Kloud Kompass! This guide will help you get started.

## Getting Started

### Prerequisites
- Python 3.9+
- AWS CLI v2 (for AWS features)
- Linux or WSL environment

### Development Setup

```bash
git clone https://github.com/MrCh0p808/KloudKompass.git
cd KloudKompass
python -m venv .venv
source .venv/bin/activate
pip install -e ".[aws,dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=kloudkompass --cov-report=term-missing

# Run a specific test file
pytest tests/test_cost_aws.py -v
```

## How to Contribute

### Reporting Bugs

1. Check existing [issues](https://github.com/MrCh0p808/KloudKompass/issues) first.
2. Include your Python version, OS, and CLI versions.
3. Provide steps to reproduce the issue.
4. Include error output with `--debug` flag if applicable.

### Suggesting Features

Open an issue with the `enhancement` label. Describe:
- The use case
- Expected behavior
- How it fits with existing features

### Submitting Pull Requests

1. Fork the repository.
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Write tests for new functionality.
4. Ensure all tests pass: `pytest`
5. Follow the existing code style.
6. Submit a PR against `main`.

## Code Style

- **Formatting:** Black (100 char line length)
- **Type hints:** Use them on all public functions
- **Docstrings:** Google-style, explaining *why* not just *what*
- **Imports:** Standard library → third-party → local, separated by blank lines
- **Module headers:** Include `© 2026 TTox.Tech. Licensed under MIT.` in new files

## Architecture Guidelines

- **Providers:** Implement `ProviderBase` subclasses in `kloudkompass/<provider>/`
- **Core abstractions:** Add new domain bases in `kloudkompass/core/`
- **TUI screens:** Extend `Screen` from `kloudkompass.tui.screens`
- **Dashboard views:** Follow the pattern in `kloudkompass/dashboard/views/`
- **Utils:** Keep utility functions stateless and well-tested

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(compute): add instance scheduling support
fix(cost): handle empty ResultsByTime from AWS
docs: update README with new CLI commands
chore: clean up stale test fixtures
```

---

*© 2026 TTox.Tech. Licensed under MIT.*
