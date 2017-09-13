#!/usr/bin/env python
import json
import logging

import PyTango
import fandango.tango as fantango

DOCUMENTATION = '''
---
module: register_device_properties

short_description: Register device properties.

description:
    - A Python script used to register TANGO device properties

options:
    element_config:
        description:
            - The config file defining the TANGO devices properties.
        required: true

author:
    - CAM (cam@ska.ac.za)
'''

EXAMPLES = '''
- name: Register the Reference Element device properties.
  register_device_properties:
    element_config: refelt_config_device_properties.json
'''

RETURN = '''
Registered_properties:
    description: The list of device properties registered in the database.
Properties_not_registered:
    description: The list of device properties not registered in the database.
'''

registered_properties = []
properties_not_registered = []


def put_device_property(device_name, device_properties):
    for property_name, property_value in device_properties.items():
        print "Setting device {} properties {}: {}".format(
            device_name, property_name, property_value)
        try:
            fantango.put_device_property(device_name, {str(property_name): property_value})
        except PyTango.DevError as deverr:
            logging.error("FAILED to register device property {} {}."
                          .format(property_name, deverr))
            print """Failed to register device property {} in the database.
                  """.format(property_name)
            properties_not_registered.append(property_name)
        else:
            print """Successfully registered device property {} in the database.
                  """.format(property_name)
            registered_properties.append(property_name)

def update_device_properties(elt_config):

    with open(elt_config) as elt_config_file:
        config_data = json.load(elt_config_file)

    devices = config_data['devices']

    for device_name, device_properties in devices.items():
        put_device_property(device_name, device_properties)


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
        Registered_properties='',
        Properties_not_registered=''
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
    update_device_properties(module.params['elt_config_file'])
    result['Registered_properties'] = registered_properties
    result['Properties_not_registered'] = properties_not_registered

    # use whatever logic you need to determine whether or not this module
    # made any modifications to your target
    if registered_properties:
        result['changed'] = True

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    if properties_not_registered:
        module.fail_json(msg='The script failed to register all the device'
                             ' properties in the TANGO db', **result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(msg="Successful run!!!", **result)



from ansible.module_utils.basic import AnsibleModule

def main():
    run_module()


if __name__ == "__main__":
    main()
