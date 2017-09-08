#!/usr/bin/env python
import json

import fandango.tango as tango


def register_device(device_name, device_class_name, server_name,
                    server_instance_name):

    svr_name = server_name + '/' + server_instance_name
    print """Attempting to register TANGO device {!r}
          class: {!r}  server: {!r}.""".format(device_name, device_class_name, svr_name)
    tango.add_new_device(svr_name, device_class_name, device_name)


def put_device_property(device_name, device_properties):

    for property_name, property_value in device_properties.items():
        print "Setting device {!r} properties {!r}: {!r}".format(
            device_name, property_name, property_value)
        tango.put_device_property(device_name, {str(property_name): [property_value]})


def main():
    with open("/home/refelt_config.json") as refelt_config_file:
        refelt_config_data = json.load(refelt_config_file)

    servers = refelt_config_data['servers']

    for server in servers:
        server_name = server['server_name']
        server_instances = server['server_instances']

        for server_instance in server_instances:
            server_instance_name = server_instance['instance_name']
            server_class = server_instance['server_class']
            class_name = server_class['class_name']
            devices = server_class['devices']

            for device in devices:
                device_name = device['device_name']
                device_properties = device['device_properties']

                register_device(device_name, class_name, server_name,
                                server_instance_name)
                put_device_property(device_name, device_properties)

if __name__ == "__main__":
    main()
