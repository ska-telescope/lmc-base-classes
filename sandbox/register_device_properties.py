#!/usr/bin/env python
import json
import argparse
import logging

import PyTango
import fandango.tango as tango


parser = argparse.ArgumentParser(
    description="A Python script used to register TANGO device properties")
parser.add_argument("-conf", "--config_file",
                    help="The config file defining the TANGO devices properties.",
                    required=True)


def put_device_property(device_name, device_properties):
    for property_name, property_value in device_properties.items():
        print "Setting device {} properties {}: {}".format(
            device_name, property_name, property_value)
        try:
            tango.put_device_property(device_name, {str(property_name): property_value})
        except PyTango.DevError as deverr:
            logging.error("FAILED to register device property {} {}."
                          .format(property_name, deverr))
            print """Failed to register device property {} in the database.
                  """.format(property_name)
        else:
            print """Successfully registered device property {} in the database.
                  """.format(property_name)

def update_device_properties(opts):

    with open(opts.config_file) as elt_config_file:
        config_data = json.load(elt_config_file)

    devices = config_data['devices']

    for device_name, device_properties in devices.items():
        put_device_property(device_name, device_properties)


def main():
    args = parser.parse_args()
    update_device_properties(args)


if __name__ == "__main__":
    main()
