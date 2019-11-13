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

	cd /app && python setup.py test | tee setup_py_test.stdout; \
	mkdir -p /build/reports; \
	mv /app/setup_py_test.stdout /build/lmcbaseclasses_setup_py_test.stdout; \
	mv /app/htmlcov /build/lmcbaseclasses_htmlcov; \
	mv /app/coverage.xml /build/reports/code-coverage.xml;

# wait for the device to be available before beginning the test
# A temporary volume is mounted at /build when 'make test' is executing.
# The following steps copy across useful output to this volume which can
# then be extracted to form the CI summary for the test procedure.
lint:
	# FIXME: At the present there is no way to extract both human readable output and JUnit XML output from pylint, as such it needs to run twice
	mkdir -p /build/reports;
	cd /app;
	pylint --rcfile=/app/.pylintrc --exit-zero --reports=y skabase > /build/reports/linting.xml;
	pylint --rcfile=/app/.pylintrc -f parseable skabase | tee /build/code_analysis.stdout

.PHONY: all test lint
