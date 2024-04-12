build: test
	python3 -m pip install --upgrade setuptools wheel build
	python3 -m build

format:
	python3 -m black src/

test: format
	.venv/bin/coverage run -m pytest
	.venv/bin/coverage report

venv: .venv
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt
	.venv/bin/pip install . 

.PHONY: test format build
