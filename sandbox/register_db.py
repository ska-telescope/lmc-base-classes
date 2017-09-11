#!/usr/bin/env python
import json
import argparse

import PyTango
import fandango.tango as tango


parser = argparse.ArgumentParser(
    description="A python scritp used to register TANGO devices and their  properties")
parser.add_argument("-conf", "--config_file",
                    help="The config file defining the TANGO devices in the Element.",
                    required=True)
registered_devices = []

def register_device(device_name, device_class_name, server_name,
                    server_instance_name):

    svr_name = server_name + '/' + server_instance_name
    print """Attempting to register TANGO device {}
          class: {}  server: {}.""".format(device_name, device_class_name, svr_name)
    try:
        tango.add_new_device(svr_name, device_class_name, device_name)
    except PyTango.DevError:
        print """Failed to register device {} due to an
              error with the database""".format(device_name)
    else:
        registered_devices.append(device_name)


def put_device_property(device_name, device_properties):

    for property_name, property_value in device_properties.items():
        print "Setting device {} properties {}: {}".format(
            device_name, property_name, property_value)
        tango.put_device_property(device_name, {str(property_name): [property_value]})


def parse_config_file(opts):

    with open(opts.config_file) as elt_config_file:
        config_data = json.load(elt_config_file)

    servers = config_data['tango_servers']

    for server in servers:
        server_name = server['server_name']
        server_instances = server['server_instances']
        for server_instance in server_instances:
            server_instance_name = server_instance['instance_name']

            device_classes = server_instance['device_classes']

            for device_class in device_classes:
                class_name = device_class['class_name']
                devices = device_class['devices']

                for device_name in devices:
                    register_device(device_name, class_name, server_name,
                                    server_instance_name)


def print_registered_devices():
    print "Device(s) successfully registered."
    print registered_devices


def main():
    args = parser.parse_args()
    parse_config_file(args)
    print_registered_devices()


if __name__ == "__main__":
    main()
