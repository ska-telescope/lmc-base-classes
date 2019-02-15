#!/usr/bin/env bash
echo "STATIC CODE ANALYSIS"
echo "===================="
echo

echo "MODULE ANALYSIS"
echo "---------------"
pylint skabase/SKAAlarmHandler/SKAAlarmHandler
pylint skabase/SKABaseDevice/SKABaseDevice
pylint skabase/SKACapability/SKACapability
pylint skabase/SKALogger/SKALogger
pylint skabase/SKAMaster/SKAMaster
pylint skabase/SKAObsDevice/SKAObsDevice
pylint skabase/SKASubarray/SKASubarray
pylint skabase/SKATelState/SKATelState

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
