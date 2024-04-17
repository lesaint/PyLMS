build: format test
	python3 -m pip install --upgrade setuptools wheel build
	python3 -m build

check-format:
	python3 -m black --check src/

format:
	python3 -m black src/ tests/

test:
	coverage run --branch -m pytest
	coverage report --fail-under=75 -m
	
venv: 
	python3 -m venv .venv
	@echo "Now run source .venv/bin/activate"

install:
	pip install -r requirements.txt
	pip install . 

.PHONY: test format build
