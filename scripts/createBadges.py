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
badge = anybadge.Badge(
    label=label, value=value, default_color=color, num_padding_chars=1
)

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
badge = anybadge.Badge(
    label=label, value=value, default_color=color, num_padding_chars=1
)

# Write badge
badge.write_badge("build/badges/build_last_date.svg", overwrite=True)

## GREEN BUILD DATE ===========================================================
# Extract metric
label = "green build"
metric = data["build-status"]["green"]["timestamp"]

timestamp = datetime.fromtimestamp(metric)
value = timestamp.strftime("%Y/%m/%d %H:%M:%S")
color = "lightgrey"

# Create badge
badge = anybadge.Badge(
    label=label, value=value, default_color=color, num_padding_chars=1
)

# Write badge
badge.write_badge("build/badges/build_green_date.svg", overwrite=True)

###############################################################################
# LINTING
## ERRORS ======================================================================
# Extract metric
## 0 for fail, 1 for pass
label = "lint errors"
metric = data["lint"]["errors"]
value = metric

# set colour
if metric == 0:
    color = "green"
elif metric > 0:
    color = "yellow"

# Create badge
badge = anybadge.Badge(
    label=label, value=value, default_color=color, num_padding_chars=1
)

# Write badge
badge.write_badge("build/badges/lint_errors.svg", overwrite=True)

## FAILURES ===================================================================
# Extract metric
## 0 for fail, 1 for pass
label = "lint failures"
metric = data["lint"]["failures"]
value = metric

# set colour
if metric == 0:
    color = "green"
elif metric > 0:
    color = "red"

# Create badge
badge = anybadge.Badge(
    label=label, value=value, default_color=color, num_padding_chars=1
)

# Write badge
badge.write_badge("build/badges/lint_failures.svg", overwrite=True)

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
    label=label,
    value=value,
    thresholds=thresholds,
    value_suffix="%",
    num_padding_chars=1,
)

# Write badge
badge.write_badge("build/badges/coverage.svg", overwrite=True)
