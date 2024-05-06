coverage_threshold = 75

build: format test
	python3 -m pip install --upgrade setuptools wheel build
	python3 -m build

check-format:
	python3 -m black --check src/

format:
	python3 -m black src/ tests/

test-run:
	coverage run --branch -m pytest

test: test-run
	coverage report --fail-under=$(coverage_threshold) --show-missing

test-ci: test-run
	coverage xml --fail-under=$(coverage_threshold)
	
venv: 
	python3 -m venv .venv
	@echo "Now run source .venv/bin/activate"

install:
	pip install -r requirements.txt
	pip install --editable .

.PHONY: test format build
