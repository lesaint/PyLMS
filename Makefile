build:
	python3 -m pip install --upgrade setuptools wheel build
	python3 -m build

venv: .venv
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt
	.venv/bin/pip install . 
