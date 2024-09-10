coverage_threshold=75

help:
	@echo 'Makefile for a PyLMS                                                                     '
	@echo '                                                                                         '
	@echo 'Usage:                                                                                   '
	@echo '   make venv            initialize venv                                                  '
	@echo '   make venvclean       delete venv                                                      '
	@echo '   make check-format    checks whether any Python file format is non compliant           '
	@echo '   make format          format all Python files with Black                               '
	@echo '   make test            run tests                                                        '
	@echo '   make test-ci         run tests in CI environment (generates XML coverage report file) '
	@echo '   make build           build artifacts                                                  '
	@echo '                                                                                         '


# use .ONESHELL to activate venv and use it across a recipe without adding it before each command (source: https://stackoverflow.com/a/55404948)
.ONESHELL:

VENV_DIR=.venv
# source: https://stackoverflow.com/a/73837995
ACTIVATE_VENV:=. $(VENV_DIR)/bin/activate

$(VENV_DIR)/touchfile: requirements.txt
	test -d "$(VENV_DIR)" || python3 -m venv "$(VENV_DIR)"
	$(ACTIVATE_VENV)
	pip install --upgrade --requirement requirements.txt
	pip install --editable .
	touch "$(VENV_DIR)/touchfile"

venv: $(VENV_DIR)/touchfile

venvclean:
	rm -rf $(VENV_DIR)

build: format test
	$(ACTIVATE_VENV)
	python3 -m pip install --upgrade setuptools wheel build
	python3 -m build

check-format: venv
	$(ACTIVATE_VENV)
	python3 -m black --check src/ tests/

format: venv
	$(ACTIVATE_VENV)
	python3 -m black src/ tests/

test-run: venv
	$(ACTIVATE_VENV)
	coverage run --branch -m pytest

test: test-run
	$(ACTIVATE_VENV)
	coverage report --fail-under=$(coverage_threshold) --show-missing

test-ci: test-run
	$(ACTIVATE_VENV)
	coverage xml --fail-under=$(coverage_threshold)

.PHONY: venv venvclean help check-format format test test-ci build
