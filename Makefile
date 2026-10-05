.PHONY: help install test lint audit names render index clean

help:
	@echo "make install  install the package in editable mode with dev tools"
	@echo "make test     run the test suite"
	@echo "make lint     run ruff"
	@echo "make audit    cross-check Wikipedia, Drive and the tracking post"
	@echo "make names    verify archive filenames against the convention"
	@echo "make render   regenerate the checklist in available-global.txt"
	@echo "make index    refresh the Drive snapshot (needs GDRIVE_API_KEY)"

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest

lint:
	ruff check .

audit:
	python -m itas.cli audit

names:
	python -m itas.cli verify-names

render:
	python -m itas.cli render --write

index:
	python -m itas.cli index --folder "$(FOLDER)"

clean:
	rm -rf build dist *.egg-info .pytest_cache .ruff_cache
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
