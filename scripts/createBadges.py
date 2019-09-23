import anybadge
import os
import sys
import json
from datetime import datetime


with open("codeMetrics.json", "r") as json_file:
    data = json.load(json_file)

###############################################################################
# BUILD STATUS
## LAST BUILD STATUS ==========================================================
# Extract metric
label = "last build"
metric = data["build-status"]["last"]["status"]
value = metric

if metric == "failed":
    # set colour
    color = "red"
elif metric == "passed":
    # set colour
    color = "green"
else:
    print("ERROR: wrong metric value")
    # set colour
    color = "yellow"

# Create badge
badge = anybadge.Badge(label=label, value=value, default_color=color, value_prefix=' ', value_suffix=' ')

# Write badge
badge.write_badge("build/badges/build_last_status.svg", overwrite=True)

## LAST BUILD DATE ===========================================================
# Extract metric
label = "last build"
metric = data["build-status"]["last"]["timestamp"]

timestamp = datetime.fromtimestamp(metric)
value = timestamp.strftime("%Y/%m/%d %H:%M:%S")
color = "lightgrey"

# Create badge
badge = anybadge.Badge(label=label, value=value, default_color=color, value_prefix=' ', value_suffix=' ')

# Write badge
badge.write_badge("build/badges/build_last_date.svg", overwrite=True)

###############################################################################
# TESTS
## FAILED ======================================================================
# Extract metric
label = "tests failed"
metric = data["tests"]["failed"]
value = metric

# set colour
if metric == 0:
    color = "green"
elif metric > 0:
    color = "red"

# Create badge
badge = anybadge.Badge(label=label, value=value, default_color=color, value_prefix=' ', value_suffix=' ')

# Write badge
badge.write_badge("build/badges/tests_failed.svg", overwrite=True)

## TOTAL ===================================================================
# Extract metric
label = "tests total"
metric = data["tests"]["total"]
value = metric

# set colour
color = "lightgrey"

# Create badge
badge = anybadge.Badge(label=label, value=value, default_color=color, value_prefix=' ', value_suffix=' ')

# Write badge
badge.write_badge("build/badges/tests_total.svg", overwrite=True)

###############################################################################
# COVERAGE
## PERCENTAGE ======================================================================
# Extract metric
label = "coverage"
metric = data["coverage"]["percentage"]
value = metric

# Define thresholds
thresholds = {50: "red", 60: "orange", 80: "yellow", 100: "green"}

# Create badge
badge = anybadge.Badge(
    label=label, value=value, thresholds=thresholds, value_format="%.2f", value_prefix=' ', value_suffix="% "
)

# Write badge
badge.write_badge("build/badges/coverage.svg", overwrite=True)

###############################################################################
# LINT
## ERRORS ======================================================================
# Extract metric
label = "lint errors"
metric = data["lint"]["errors"]
value = metric

# set colour
if metric == 0:
    color = "green"
elif metric > 0:
    color = "yellow"

# Create badge
badge = anybadge.Badge(label=label, value=value, default_color=color, value_prefix=' ', value_suffix=' ')

# Write badge
badge.write_badge("build/badges/lint_errors.svg", overwrite=True)

## FAILURES ===================================================================
# Extract metric
label = "lint failures"
metric = data["lint"]["failures"]
value = metric

# set colour
if metric == 0:
    color = "green"
elif metric > 0:
    color = "red"

# Create badge
badge = anybadge.Badge(label=label, value=value, default_color=color, value_prefix=' ', value_suffix=' ')

# Write badge
badge.write_badge("build/badges/lint_failures.svg", overwrite=True)

## NO. TESTS ===================================================================
# Extract metric
label = "lint tests"
metric = data["lint"]["tests"]
value = metric

# set colour
color = "lightgrey"

# Create badge
badge = anybadge.Badge(label=label, value=value, default_color=color, value_prefix=' ', value_suffix=' ')

# Write badge
badge.write_badge("build/badges/lint_tests.svg", overwrite=True)
