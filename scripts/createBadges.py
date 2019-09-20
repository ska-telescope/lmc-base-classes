import anybadge
import os
import sys
import json

with open("codeMetrics.json", "r") as json_file:
    data = json.load(json_file)

###############################################################################
# BUILD STATUS
## LAST BUILD

# Extract metric
## 0 for fail, 1 for pass
label = "last build"
metric = data["build-status"]["latest"]["status"]

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

###############################################################################
# LINTING

# Extract metric
## 0 for fail, 1 for pass
label = "lint errors"
metric = data["linting"]["errors"]

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


# # Define thresholds
# build_s_t = { 0: "red",
#               1: "green"
#               }