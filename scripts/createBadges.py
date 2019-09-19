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
metric = data["build-status"]["latest"]["status"]

if metric == 0:
    # set text
    metric_value = "failed"
    # set colour
    metric_color = "red"
elif metric == 1:
    # set text
    metric_value = "passed"
    # set colour
    metric_color = "green"
else:
    print("ERROR: wrong metric value")
    sys.exit()

# Create badge
badge = anybadge.Badge(label='last build', value=metric_value, default_color=metric_color)

# Write badge
badge.write_badge('build/badges/last_build_s.svg')

###############################################################################

# # Define thresholds
# build_s_t = { 0: "red",
#               1: "green"
#               }