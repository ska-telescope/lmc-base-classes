#!/usr/bin/env python
import json
import argparse
import logging

import PyTango
import fandango.tango as tango


parser = argparse.ArgumentParser(
    description="A Python script used to register TANGO devices to the database")
parser.add_argument("-conf", "--config_file",
                    help="The config file defining the TANGO devices in the Element.",
                    required=True)


def register_devices(device_class_name, server_name, server_instance_name,
                     devices_list=None):

    if devices_list is None:
        print """No device(s) to register for server: {}, server_instance: {}, class: {}
              """.format(server_name, server_instance_name, device_class_name)
        return
    elif not isinstance(devices_list, list):
        devices_list = [devices_list]

    svr_name = server_name + '/' + server_instance_name

    for device_name in devices_list:
        print """Attempting to register TANGO device {}
               class: {} server: {}.""".format(device_name, device_class_name, svr_name)
        try:

            tango.add_new_device(svr_name, device_class_name, device_name)
        except PyTango.DevError as deverr:
            logging.error("FAILED to register device {} {}".
                          format(device_name, deverr))
            print """Failed to register device {} due to an error with the database.
                  """.format(device_name)
        else:
            print """Successfully registered device {} in the database.
                  """.format(device_name)


def register_element(opts):

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

                register_devices(class_name, server_name, server_instance_name, devices)


def main():
    args = parser.parse_args()
    register_element(args)


if __name__ == "__main__":
    main()
