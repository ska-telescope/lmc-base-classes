all: test

# wait for the device to be available before beginning the test
# A temporary volume is mounted at /build when 'make test' is executing.
# The following steps copy across useful output to this volume which can
# then be extracted to form the CI summary for the test procedure.
test:
	retry -- tango_admin --check-device ska/BaseDevice/01
	cd /app && python setup.py test | tee setup_py_test.stdout
#	cd /app && ./code-analysis.sh | tee code_analysis.stdout
#	if [ -d /build ]; then \
#		mv /app/setup_py_test.stdout /build; \
#		mv /app/code_analysis.stdout /build; \
#		mv /app/htmlcov /build; \
#		mv /app/coverage.xml /build; \
#	fi;

.PHONY: all test
