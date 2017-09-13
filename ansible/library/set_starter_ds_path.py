#!/usr/bin/env python

import sys
import PyTango
import platform



##################################################
###          MODULE MAIN
##################################################
def main():
    """Main for the Ansible module"""

    ## Create ansible module
    changed = False
    message = ''

    module = AnsibleModule(
        argument_spec=dict(
            facility_name=dict(required=True),
            facility_config=dict(required=True),
            add_path=dict(required=True)),
        supports_check_mode=True
        )

    # In check mode, we take no action
    # Since this module never changes system state, we just
    # return changed=False
    if module.check_mode:
        module.exit_json(changed=False)

    errors = 0
    db  = PyTango.Database()
    add_path = module.params.get('add_path')

    try:
        hostname = platform.uname()[1]
        starter = "tango/admin/" + hostname
        curr_dspath = db.get_device_property_list(starter, "startDsPath").value_string
        db.put_device_property(starter, {"startDsPath": curr_dspath.extend([add_path])})
        out = db.get_device_property_list(starter, "startDsPath").value_string
    except Exception as exc:
        msg = "FAILED ({})".format(exc)
        errors += 1

    if errors:
        module.fail_json(msg=msg)
    else:
        module.exit_json(msg="Success (startDsPath={})".format(out),changed=True)


## Include at the end ansible (NB: it is not a standard Python include according to manual)
from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
