#!/usr/bin/env python

import PyTango
import platform



##################################################
###          MODULE MAIN
##################################################
def main():
    """Main for the Ansible module"""

    ## Create ansible module
    module = AnsibleModule(
        argument_spec=dict(
            starter_path=dict(required=True)),
        supports_check_mode=True
        )

    # In check mode, we take no action
    # Since this module never changes system state, we just
    # return changed=False
    if module.check_mode:
        module.exit_json(changed=False)

    errors = 0
    db  = PyTango.Database()
    starter_path = module.params.get('starter_path')

    try:
        hostname = platform.uname()[1]
        starter = "tango/admin/" + hostname
        path_list = starter_path.split(",")
        db.put_device_property(starter, {"StartDsPath": path_list})
        out = db.get_device_property(starter, "StartDsPath")
        # Re-initialise Starter for the path to take effect
        dp = PyTango.DeviceProxy(starter)
        dp.command_inout("init")
    except Exception as exc:
        msg = "FAILED ({})".format(exc)
        errors += 1

    if errors:
        module.fail_json(msg=msg, changed=True) # May be no change, but rather say True if not sure
    else:
        module.exit_json(msg="Success ({})".format(out), changed=True)


## Include at the end ansible (NB: it is not a standard Python include according to manual)
from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
