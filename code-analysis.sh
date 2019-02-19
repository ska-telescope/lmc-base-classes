#!/usr/bin/env bash
echo "STATIC CODE ANALYSIS"
echo "===================="
echo

echo "MODULE ANALYSIS"
echo "---------------"
pylint --rcfile=rcfile skabase

echo "TESTS ANALYSIS"
echo "--------------"
pylint --rcfile=rcfile skabase/SKAAlarmHandler/test
pylint --rcfile=rcfile skabase/SKABaseDevice/test
pylint --rcfile=rcfile skabase/SKACapability/test
pylint --rcfile=rcfile skabase/SKALogger/test
pylint --rcfile=rcfile skabase/SKAMaster/test
pylint --rcfile=rcfile skabase/SKAObsDevice/test
pylint --rcfile=rcfile skabase/SKASubarray/test
pylint --rcfile=rcfile skabase/SKATelState/test
