.DEFAULT_GOAL := help
PYTHON ?= python3

.PHONY: help setup test frontend-test

help:
	@printf '%s\n' 'make setup          Report local tool availability' 'make test           Run repository tests' 'make frontend-test  Build the React frontend'

setup:
	bash setup.sh

test:
	bash -n setup.sh
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py' -v
	$(PYTHON) -m pytest -q tests/test_services.py

frontend-test:
	cd frontend && npm run build
