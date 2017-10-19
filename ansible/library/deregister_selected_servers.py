#!/usr/bin/python
import json
import logging

import fandango as fn
import PyTango

DOCUMENTATION = '''
---
module: start_element

short_description: Start element device servers.

description:
    - Start the device servers in the element using Astor.

options:
    element_config:
        description:
            - A json file defining the list of device server instances grouped
              according to their startup levels.
        required: true

author:
    - CAM (cam@ska.ac.za)
'''

EXAMPLES = '''
- name: Start the Element's device servers.
  start_element:
    element_config: refelt_config_starter.json
'''

RETURN = '''
success_output:
    : The list of server instances processed successfully.
failed_output:
    : The list of server instances for which processing failed.
'''

success_output = []
failed_output = []
skipped_output = []


def stop_servers(startswith_list):

    astor = fn.Astor()

    db = PyTango.Database()
    datum = db.get_server_list()
    
    for server_instance in datum.value_string:
        # Operate on servers starting with the specified strings
        items = [item for item in startswith_list if server_instance.startswith(item)]
        if items:
            try:
                #db.delete_server(server_instance)
                #success_output.append(server_instance)
                failed_output.append(server_instance+"(NO-OP IN DELETING:{})".format(exc))
            except Exception as exc:
                logging.error("EXCEPTION in deleting {} {}".format(
                    server_instance, exc))
                failed_output.append(server_instance+"(EXC IN DELETING:{})".format(exc))
        else:
            skipped_output.append(server_instance+" (SKIPPED)")


def delete_servers(startswith_list):

    db = PyTango.Database()
    datum = db.get_server_list()
    
    for server_instance in datum.value_string:
        # Operate on servers starting with the specified strings
        items = [item for item in startswith_list if server_instance.startswith(item)]
        if items:
            try:
                db.delete_server(server_instance)
                success_output.append(server_instance)
            except Exception as exc:
                logging.error("EXCEPTION in deleting {} {}".format(
                    server_instance, exc))
                failed_output.append(server_instance+"(EXC IN DELETING:{})".format(exc))
        else:
            skipped_output.append(server_instance+" (SKIPPED)")

def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    # do_what can be:
    #    "stop_servers" to stop servers in Astor, or
    #    "delete_servers" to delete servers from TANGO DB
    module_args = dict(
        do_what=dict(type='str', required=True),
        startswith=dict(type='str', required=True)
    )

    # seed the result dict in the object
    result = dict(
        changed=False,
        success_output='',
        failed_output=''
    )
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        return result

    # manipulate or modify the state as needed
    if module.params['do_what'] == "stop_servers":
        stop_servers(module.params['startswith'].split(","))
    elif module.params['do_what'] == "delete_servers":
        delete_servers(module.params['startswith'].split(","))
    result['success_output'] = success_output + skipped_output
    result['failed_output'] = failed_output

    # use whatever logic you need to determine whether or not this module
    # made any modifications to your target
    if success_output:
        result['changed'] = True

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    if failed_output:
        module.fail_json(msg='The script failed to {} all the servers'.format(module.params['do_what']),
                         **result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(msg="Successful run!!!", **result)


from ansible.module_utils.basic import AnsibleModule

def main():
    run_module()

if __name__ == '__main__':
    main()
