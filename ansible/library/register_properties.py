#!/usr/bin/env python
import json
import logging
import fandango

import PyTango
import fandango.tango as fantango

DOCUMENTATION = '''
---
module: register_properties

short_description: Register global and device properties.

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
  register_properties:
    config_json: config_properties.json
'''

RETURN = '''
Registered_properties:
    description: The list of device properties registered in the database.
Properties_not_registered:
    description: The list of device properties not registered in the database.
'''

registered_properties = []
properties_not_registered = []


def put_properties(property_type, target_name, properties):
    """
    A generic helper function used to register properties in the TANGO database.

    Parameters
    ----------
    property_type: str
        The type of property (device, class, or free).
    target_name: str
        The target which the property is going to be registered against. Either the
        device-name, class-name or the name of the free property.
    properties: dict
        A collection of the property names and property values.
    """
    for property_name, property_value in properties.items():
        print "Setting {} properties {}: {}".format(
            property_type, property_name, property_value)

        try:
            if fandango.functional.isSequence(property_value):
                property_values = []
                for prop in property_value:
                    property_values.append(json.dumps(prop))
                prop_val = property_values
            else:
                prop_val = property_value

            fun = getattr(fantango, 'put_{}_property'.format(property_type))
            fun(target_name, {str(property_name): prop_val})
        except PyTango.DevError as deverr:
            logging.error("FAILED to register {} property {} {}."
                          .format(property_type, property_name, deverr))
            print """Failed to register device property {} in the database.
                  """.format(property_name)
            properties_not_registered.append("/".join([target_name, property_name]))
        else:
            print """Successfully registered {} property {} in the database.
                  """.format(property_type, property_name)
            registered_properties.append("/".join([target_name, property_name]))


def update_database_properties(config_data):

    global_property_name = 'telescope'

    for property_type in config_data:
        if property_type == 'devices':
            for device_name, device_properties in config_data[property_type].items():
                put_property('device', device_name, device_properties)
        elif property_type == 'classes':
            for class_name, class_properties in config_data[property_type].items():
                put_property('class', class_name, class_properties)
        elif property_type == 'global':
            put_property('free', global_property_name, config_data[property_type])


def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    module_args = dict(
        properties_file=dict(type='str', required=False),
        properties_json=dict(type='str', required=False)
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

    # Load config from file or json
    if module.params['properties_json']:
        config_data = json.loads(module.params['properties_json'])
        update_database_properties(config_data)
    elif module.params['properties_file']:
        config_file = module.params['properties_file']
        with open(config_file) as config_fileh:
            config_data = json.load(config_fileh)
            update_database_properties(config_data)
    else:
        module.fail_json(msg='Required parameter properties_json or properties_file'
                             ' is missing', **result)

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
