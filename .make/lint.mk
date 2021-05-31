
_format-lint-install:  # install requirements for code formatting and checking
	python3 -m pip install -r requirements-lint.txt

.PHONY: _format-lint-install


format: _format-lint-install  # apply code formatting
	black src/ tests/

lint: _format-lint-install
	mkdir -p build/reports
	- python3 -m flake8 --format=junit-xml --output-file=build/reports/linting.xml src/ tests/
	python3 -m flake8 --statistics --show-source src/ tests/

# Format code then lint it
format-lint: format lint

.PHONY: format lint format-lint
