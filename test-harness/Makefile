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
	if [ -d /build ]; then \
		mv /app/setup_py_test.stdout /build/lmcbaseclasses_setup_py_test.stdout; \
		mv /app/htmlcov /build/lmcbaseclasses_htmlcov; \
		mv /app/coverage.xml /build/lmcbaseclasses_coverage.xml; \
	fi;

# wait for the device to be available before beginning the test
# A temporary volume is mounted at /build when 'make test' is executing.
# The following steps copy across useful output to this volume which can
# then be extracted to form the CI summary for the test procedure.
lint:
	retry --max=10 -- tango_admin --ping-device ska/basedevice/01
	retry --max=10 -- tango_admin --ping-device ska/alarmhandler/01
	retry --max=10 -- tango_admin --ping-device ska/capability/01
	retry --max=10 -- tango_admin --ping-device ska/logger/01
	retry --max=10 -- tango_admin --ping-device ska/master/01
	retry --max=10 -- tango_admin --ping-device ska/obsdevice/01
	retry --max=10 -- tango_admin --ping-device ska/subarray/01
	retry --max=10 -- tango_admin --ping-device ska/telstate/01

	# FIXME pylint needs to run twice since there is no way go gather the text and junit xml output at the same time
	cd /app && pylint -f colorized skabase | tee code_analysis.stdout; \
	cd /app && pylint skabase > lint_output.xml; \
	if [ -d /build ]; then \
		mv /app/code_analysis.stdout /build/lmcbaseclasses_code_analysis.stdout; \
		mv /app/lint_output.xml /build/lint_output.xml; \
	fi;

.PHONY: all test lint
