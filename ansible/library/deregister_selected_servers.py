#!/usr/bin/python
import json
import logging

import fandango as fn
import PyTango

DOCUMENTATION = '''
---
module: deregister all servers starting with the items listed

short_description: Deregister selected servers

description:
    - Deregister servers starting with specified items from TANGO DB and Astor.

options:
    do_what:
        description:
            - Either "stop_servers" or "delete_servers". To stop servers in Astor
              or delete servers in Tango DB.
        required: true
        
    startswith:
        description:
            - Comma delimited list of items to match server names. Only servers starting
              with any of the items in the list will be processed.
        required: true
        

author:
    - CAM (cam@ska.ac.za)
'''

EXAMPLES = '''
- name: Delete RefEltN servers
  deregister_selected_servers:
    do_what: "delete_servers"
    startswith: "SvrRef"
'''

RETURN = '''
success_output:
    : The list of servers processed successfully.
failed_output:
    : The list of servers for which processing failed.
skipped_output:
    : The list of servers for which processing were skipped.
'''

success_output = []
failed_output = []
skipped_output = []


def stop_servers(startswith_list):

    astor = fn.Astor()

    db = PyTango.Database()
    datum = db.get_server_list()
    
    for server_name in datum.value_string:
        # Operate on servers starting with the specified strings
        items = [item for item in startswith_list if server_name.startswith(item)]
        if items:
            try:
                # TBD - add the 
                # astor.stop_server(server_name)
                # success_output.append(server_name)
                failed_output.append(server_name+"(NO-OP IN STOPPING:{})".format(exc))
            except Exception as exc:
                logging.error("EXCEPTION in stopping {} {}".format(
                    server_name, exc))
                failed_output.append(server_name+"(EXC IN STOPPING:{})".format(exc))
        else:
            skipped_output.append(server_name+" (SKIPPED)")


def delete_servers(startswith_list):

    db = PyTango.Database()
    datum = db.get_server_list()
    
    for server_name in datum.value_string:
        # Operate on servers starting with the specified strings
        items = [item for item in startswith_list if server_name.startswith(item)]
        if items:
            try:
                db.delete_server(server_name)
                success_output.append(server_name)
            except Exception as exc:
                logging.error("EXCEPTION in deleting {} {}".format(
                    server_name, exc))
                failed_output.append(server_name+"(EXC IN DELETING:{})".format(exc))
        else:
            skipped_output.append(server_name+" (SKIPPED)")

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
        skipped_output='',
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
    result['success_output'] = success_output
    result['skipped_output'] = skipped_output
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
