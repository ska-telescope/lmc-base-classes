
_lint-install:  # install requirements for linting
	python3 -m pip install -r requirements-lint.txt

_lint-format-apply: _lint-install  # apply code formatting
	black src/ tests/

_lint-format-check: _lint-install  # check code has been formatted
	black --check src/ tests/

_lint-other-checks: _lint-install  # all other checks
	mkdir -p build/reports
	pylint --output-format=parseable src/ska_tango_base | tee build/code_analysis.stdout
	pylint --output-format=pylint2junit.JunitReporter src/ska_tango_base > build/reports/linting.xml

.PHONY: _lint-install _lint-format-apply _lint-format-check _lint-other-checks


# Check code has been formatted, then check everything else
lint-check: _lint-format-check _lint-other-checks

# Actively format code, then check everything else
lint: _lint-format-apply _lint-other-checks

.PHONY: lint-check lint
