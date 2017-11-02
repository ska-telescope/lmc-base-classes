#!/usr/bin/env python
import json
import logging

import PyTango
import fandango.tango as fantango

DOCUMENTATION = '''
---
module: register_element

short_description: Register TANGO devices.

description:
    - This module is used to register TANGO devices of an Element to the database.

options:
    element_config:
        description:
            - A json file defining the list of devices in an element.
        required: true

author:
    - CAM (cam@ska.ac.za)
'''

EXAMPLES = '''
- name: Register the Reference Element devices.
  register_element:
    element_config: refelt_config_db.json
'''

RETURN = '''
Registered_devices:
    description: The list of devices registered in the database.
Devices_not_registered:
    description: The list of devices not registered in the database.
'''

registered_devices = []
devices_not_registered = []

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

            fantango.add_new_device(svr_name, device_class_name, device_name)
        except PyTango.DevError as deverr:
            logging.error("FAILED to register device {} {}".
                          format(device_name, deverr))
            print """Failed to register device {} due to an error with the database.
                  """.format(device_name)
            devices_not_registered.append("{}({})".format(device_name, svr_name))
        else:
            print """Successfully registered device {} in the database.
                  """.format(device_name)
            registered_devices.append(device_name+"({})".format(svr_name))


def register_element(config_file):

    with open(config_file) as elt_config_file:
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


def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    module_args = dict(
        elt_config_file=dict(type='str', required=True)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task.
    result = dict(
        changed=False,
        Registered_devices='',
        Devices_not_registered=''
    )
    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode.
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        return result

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    register_element(module.params['elt_config_file'])
    result['Registered_devices'] = registered_devices
    result['Devices_not_registered'] = devices_not_registered

    # use whatever logic you need to determine whether or not this module
    # made any modifications to your target
    if registered_devices:
        result['changed'] = True

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    if devices_not_registered:
        module.fail_json(msg='The script failed to register all the devices in'
                             ' the TANGO db', **result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(msg="Successful run!!!", **result)


from ansible.module_utils.basic import AnsibleModule

def main():
    run_module()

if __name__ == '__main__':
    main()
