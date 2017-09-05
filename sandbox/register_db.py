#!/usr/bin/env python

import logging
import json
import pkg_resources

import PyTango

def register_device(name, device_class, server_name, instance):
    dev_info = PyTango.DbDevInfo()
    dev_info.name = name
    dev_info._class = device_class
    dev_info.server = "{}/{}".format(server_name.split('.')[0], instance)
    print """Attempting to register TANGO device {!r}
    class: {!r}  server: {!r}.""".format(
            dev_info.name, dev_info._class, dev_info.server)
    db = PyTango.Database()
    db.add_device(dev_info)

def put_device_property(device_name, device_properties):
    db = PyTango.Database()
    for property_name, property_value in device_properties.items():
        print "Setting device {!r} properties {!r}: {!r}".format(
            device_name, property_name, property_value)
        db.put_device_property(device_name, {str(property_name):[property_value]})
print "Running script from ansible playbook."


with open("refelt_config.json") as config_file:
    device_data = json.load(config_file)

server_data = device_data['servers']

for server in server_data:
    server_name = server['server_name']
    server_instance = server['server_instance']
    
    
    devices = server['devices']
    for device in devices:
        class_name = device['class_name']
        device_name = device['device_name']
        device_properties = device['device_properties']

        register_device(device_name, class_name, server_name, server_instance)
        put_device_property(device_name, device_properties)

    
