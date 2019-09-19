import anybadge
import os
import sys
import json

with open("codeMetrics.json", "r") as json_file:
    data = json.load(json_file)

# Define thresholds
build_s_t = { 0: "red",
              1: "green"
              }

# Extract metric
last_build_s_m = data["build-status"]["latest"]["status"]

# Create badge
last_build_s_b = anybadge.Badge('last build', last_build_s_m, thresholds=build_s_t)

# Write badge
last_build_s_b.write_badge('public/badges/last_build_s.svg')

