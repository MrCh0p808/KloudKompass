# Makefile for Kloud Kompass
# -------------------------
# © 2026 TTox.Tech. Licensed under MIT.

.PHONY: setup test coverage lint build clean

setup:
	pip install -e ".[dev,aws]"

test:
	pytest -v

coverage:
	pytest --cov=kloudkompass --cov-report=term-missing

lint:
	black --check kloudkompass tests
	mypy kloudkompass

format:
	black kloudkompass tests

build: clean
	python -m build

clean:
	rm -rf dist/ build/ *.egg-info .pytest_cache .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
