#!/usr/bin/env bash
echo "STATIC CODE ANALYSIS"
echo "===================="
echo

# FIXME pylint needs to run twice since there is no way go gather the text and xml output at the same time
pylint -f colorized skabase
pylint skabase > lint_output.xml