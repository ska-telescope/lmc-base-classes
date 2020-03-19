# Use bash shell with pipefail option enabled so that the return status of a
# piped command is the value of the last (rightmost) commnand to exit with a
# non-zero status. This lets us pipe output into tee but still exit on test
# failures.
SHELL = /bin/bash
.SHELLFLAGS = -o pipefail -c

all: test lint

# wait for the device to be available before beginning the test
# A temporary volume is mounted at /build when 'make test' is executing.
# The following steps copy across useful output to this volume which can
# then be extracted to form the CI summary for the test procedure.
test:
	retry --max=10 -- tango_admin --ping-device ska/basedevice/01
	retry --max=10 -- tango_admin --ping-device ska/alarmhandler/01
	retry --max=10 -- tango_admin --ping-device ska/capability/01
	retry --max=10 -- tango_admin --ping-device ska/logger/01
	retry --max=10 -- tango_admin --ping-device ska/master/01
	retry --max=10 -- tango_admin --ping-device ska/obsdevice/01
	retry --max=10 -- tango_admin --ping-device ska/subarray/01
	retry --max=10 -- tango_admin --ping-device ska/telstate/01

	cd /app && python setup.py test | tee setup_py_test.stdout && \
	mkdir -p /build/reports && \
	mv /app/setup_py_test.stdout /build/lmcbaseclasses_setup_py_test.stdout && \
	mv /app/htmlcov /build/lmcbaseclasses_htmlcov && \
	mv /app/coverage.xml /build/reports/code-coverage.xml

# wait for the device to be available before beginning the test
# A temporary volume is mounted at /build when 'make test' is executing.
# The following steps copy across useful output to this volume which can
# then be extracted to form the CI summary for the test procedure.
# FIXME: Add pylint2junit to the tango-builder:latest image so that we don't need to install it here.
# FIXME: Missing functionality in pylint2junit prevents converting from parseable to xml. Once it's implemented there is no need to run linting twice.
lint:
	python3 -m pip install pylint2junit; \
	mkdir -p /build/reports; \
	cd /app && pylint --output-format=parseable src/ska | tee /build/code_analysis.stdout; \
	cd /app && pylint --output-format=pylint2junit.JunitReporter src/ska > /build/reports/linting.xml;

.PHONY: all test lint
