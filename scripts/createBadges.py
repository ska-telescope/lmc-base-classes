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
## 0 for fail, 1 for pass
label = "last build"
metric = data["build-status"]["last"]["status"]

if metric == 0:
    # set text
    value = "failed"
    # set colour
    color = "red"
elif metric == 1:
    # set text
    value = "passed"
    # set colour
    color = "green"
else:
    print("ERROR: wrong metric value")
    sys.exit()

# Create badge
badge = anybadge.Badge(label=label, value=value, default_color=color)

# Write badge
badge.write_badge('build/badges/build_last_status.svg')

## LAST BUILD DATE ===========================================================
# Extract metric
label = "last build"
metric = data["build-status"]["last"]["timestamp"]

timestamp = datetime.fromtimestamp(metric)
value = timestamp.strftime("%Y/%m/%d %H:%M:%S")
color = "lightgrey"

# Create badge
badge = anybadge.Badge(label=label, value=value, default_color=color)

# Write badge
badge.write_badge('build/badges/build_last_date.svg')

## GREEN BUILD DATE ===========================================================
# Extract metric
label = "green build"
metric = data["build-status"]["green"]["timestamp"]

timestamp = datetime.fromtimestamp(metric)
value = timestamp.strftime("%Y/%m/%d %H:%M:%S")
color = "lightgrey"

# Create badge
badge = anybadge.Badge(label=label, value=value, default_color=color)

# Write badge
badge.write_badge('build/badges/build_green_date.svg')

###############################################################################
# LINTING
## ERRORS ======================================================================
# Extract metric
## 0 for fail, 1 for pass
label = "lint errors"
metric = data["lint"]["errors"]

if metric == 0:
    # set text
    value = metric
    # set colour
    color = "green"
elif metric > 0:
    # set text
    value = metric
    # set colour
    color = "yellow"

# Create badge
badge = anybadge.Badge(label=label, value=value, default_color=color)

# Write badge
badge.write_badge('build/badges/lint_errors.svg')

## FAILURES ===================================================================
# Extract metric
## 0 for fail, 1 for pass
label = "lint failures"
metric = data["lint"]["failures"]

if metric == 0:
    # set text
    value = metric
    # set colour
    color = "green"
elif metric > 0:
    # set text
    value = metric
    # set colour
    color = "red"

# Create badge
badge = anybadge.Badge(label=label, value=value, default_color=color)

# Write badge
badge.write_badge('build/badges/lint_failures.svg')

###############################################################################
# COVERAGE
## PERCENTAGE ======================================================================
# Extract metric
label = "coverage"
metric = data["coverage"]["percentage"]
value = metric

# Define thresholds
thresholds = {50: 'red',
              70: 'orange',
              80: 'yellow',
              90: 'green'}

# Create badge
badge = anybadge.Badge(label=label, value=value, thresholds=thresholds)

# Write badge
badge.write_badge('build/badges/coverage.svg')
