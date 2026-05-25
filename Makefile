.PHONY: install test coverage run

install:
	pip install -r requirements-dev.txt -r scraper/requirements.txt

test:
	python -m pytest tests/

coverage:
	python -m pytest tests/ --cov=scraper --cov-report=term-missing

run:
	python scraper/main.py
