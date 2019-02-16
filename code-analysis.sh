#!/usr/bin/env bash
echo "STATIC CODE ANALYSIS"
echo "===================="
echo

echo "MODULE ANALYSIS"
echo "---------------"
pylint --rcfile=rcfile skabase

echo "TESTS ANALYSIS"
echo "--------------"
pylint skabase/SKAAlarmHandler/test
pylint skabase/SKABaseDevice/test
pylint skabase/SKACapability/test
pylint skabase/SKALogger/test
pylint skabase/SKAMaster/test
pylint skabase/SKAObsDevice/test
pylint skabase/SKASubarray/test
pylint skabase/SKATelState/test
