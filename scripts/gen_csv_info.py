#!/usr/bin/env python

"""A utility script we can make use of to convert the xmi files to a simple csv file."""


import csv
import subprocess

from tango_simlib import sim_xmi_parser

# Find the xmi files in the repo and store their paths
output = subprocess.check_output(["kat-search.py -f *.xmi"], shell=True)

# Create a list of of all the file paths.
strings = output.split("\n")
# Remove the string "DEFAULT", which is always the first output of 'kat-search.py'.
strings.remove("DEFAULTS")

# Create a csv file object.
with open("csv_file.csv", 'wb') as myfile:
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    print csv.QUOTE_ALL
    for fiel in strings:
       
        xmi_parser = sim_xmi_parser.XmiParser()
        try:
            xmi_parser.parse(fiel)
        except AttributeError:
            continue
        
        print fiel 
        attr_info = xmi_parser.get_reformatted_device_attr_metadata()
        #cmd_info = xmi_parser.get_reformatted_cmd_metadata()
        #dev_props = xmi_parser.get_reformatted_properties_metadata('deviceProperties')
        #class_props = xmi_parser.get_reformatted_properties_metadata('classProperties')
        for attr_name, attr_props in attr_info.items():
            print attr_props

            
            break

        del xmi_parser
        break

        
    
    
