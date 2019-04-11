#!/usr/bin/env bash
echo "STATIC CODE ANALYSIS"
echo "===================="
echo

echo "MODULE ANALYSIS"
echo "---------------"
pylint --rcfile=.pylintrc skabase

echo "TESTS ANALYSIS"
echo "--------------"
pylint --rcfile=.pylintrc skabase/SKAAlarmHandler/test
pylint --rcfile=.pylintrc skabase/SKABaseDevice/test
pylint --rcfile=.pylintrc skabase/SKACapability/test
pylint --rcfile=.pylintrc skabase/SKALogger/test
pylint --rcfile=.pylintrc skabase/SKAMaster/test
pylint --rcfile=.pylintrc skabase/SKAObsDevice/test
pylint --rcfile=.pylintrc skabase/SKASubarray/test
pylint --rcfile=.pylintrc skabase/SKATelState/test
