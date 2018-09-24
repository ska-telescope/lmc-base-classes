# Deployment Notes
Old notes for LEvPRo deployment can be found in:
[LEvPro Deployment Notes](https://docs.google.com/document/d/12f495FEMOi0g3bJjoZL3icZaCCr7iSjTY3jToFqA2Ns/edit#)

# To get going with a fresh node (Docker container):

## Run a Docker container:
Follow the steps in `../docker/README.md`.  Launch the docker with the lmc-base-classes project mounted inside the container.

Obviously any changes made inside the container, e.g. software installed, will not persist.  Images can be made from a running container, if you want to keep changes (read the Docker docs).  Note that changes to the files in the lmc-base-classes project will persist, because these files live on the host machine, and are just mounted inside the container.  

## Install the lmc-base-classes python modules and register TANGO devices
```
cd ~/src/lmc-base-classes/ansible
./play-task.sh generate-sw-refelt-simlib
./play-task.sh install-sw
./play-task.sh register-my-refelt local  # startup can take 5 minutes!
```

Note: `register-refelt` is deprecated.

## Updating after .xmi file changes (POGO generation)
```
cd ~/src/lmc-base-classes
purge_xmi_tree.py --path .
cd ~/src/lmc-base-classes/ansible
./play-task.sh deregister_refelts.yml
./play-task.sh generate-sw
./play-task.sh install-sw
./play-task.sh register-my-refelt local
```

Notes:
- license file text may need to be updated in POGO generated files.
- The deregister_refelts.yml role removes registrations in Tango DB and Astor so that
  we can start again, with nothing registered.

# To get going with a fresh Ubuntu 14.04 system (not recommended!):

If you don't have Docker, you could try a virtual machine. The ansible playbooks and instructions below have only been used on Ubuntu 14.04, so your mileage may vary on other versions of Linux.

## Install latest version of pip (required on Ubuntu 14.04):
Old Ubuntu packages cause an issue, so remove manually.  Can't easily be done using Ansible, since removing the Python packages removes ansible while it is running!
```
sudo apt-get remove -y python-setuptools python-pkg-resources
cd /tmp
wget --no-check-certificate https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py
rm get-pip.py
cd
```

## Add this apt repo to get recent version of ansible (>=2.3.2)
## Needed on Ubuntu 14.04, might not be required on later releases

```
sudo add-apt-repository ppa:ansible/ansible
sudo apt-get update
sudo apt-get install ansible
mkdir ~/src
git clone https://github.com/ska-telescope/lmc-base-classes ~/src/lmc-base-classes
```

## Deploy tangobox and a lmc-base-classes RefElt on a fresh node
```
cd ~/src/lmc-base-classes/ansible
./play-task.sh deploy-tangobox
./play-task.sh deploy-sw
./play-task.sh generate-sw
./play-task.sh install-sw
./play-task.sh register-my-refelt local
Optional:
./play-task.sh register-my-refelt devXn
./play-task.sh deregister_refelts.yml
```

## Updating after .xmi file changes (POGO generation)
```
cd ~/src/lmc-base-classes
purge_xmi_tree.py --path .
cd ~/src/lmc-base-classes/ansible
./play-task.sh deregister_refelts.yml
./play-task.sh generate-sw
./play-task.sh install-sw
./play-task.sh register-my-refelt local
```

# play-task - A utility to run a single specific task
(based on ROLE tags and TASK IDs described in NOTES below)

To see all task tags execute:
```
./play-task.sh
```

To run a full role (use the ROLE name)
```
./play-task.sh install-sw
or
./play-task.sh refresh_sw
```

To run a specific task (use ROLE tags plus TASK ID)
```
./play-task.sh install-sw-skabase
or
./play-task.sh deploy-tangobox-start-tango
```

The above all run the site.yml playbook with "--limit local".

To run on specific hosts, update hosts file and then specific a hosts group like this:
```
./play-task.sh install-sw devXX
or
./play-task.sh install-sw-skabase refelt
```

## To run a role

To see all playbooks exposing the roles:
```
ls -la *.yml
```

To run the role, run the playbook like any of the lines below:
```
./play-task.sh install-sw
./play-task.sh refresh-sw devXX
```
or using ansible-playbook directly
```
ansible-playbook -i hosts install_sw.yml --list-tags [--limit devXX]
ansible-playbook -i hosts install_sw.yml --list-hosts [--limit devXX]
ansible-playbook -i hosts install_sw.yml
ansible-playbook -i hosts install_sw.yml -t install-sw-lmc-base-classes
```

### To deploy SW on local: # Git clone if not available, else git pull
```
./play-task.sh deploy-sw
```
or using ansible-playbook directly
```
ansible-playbook -i hosts site.yml --limit local --tags "deploy-sw"
```

### To refresh SW on local: # Git pull
```
./play-task.sh refresh-sw
./play-task.sh refresh-sw-lmc-base-classes
```
or using ansible-playbook directly
```
ansible-playbook -i hosts site.yml --limit local --tags "refresh-sw"
ansible-playbook -i hosts site.yml --limit local --tags "refresh-sw-lmc-base-classes"
```

### To install SW on local: # sudo pip install
```
./play-task.sh install-sw
./play-task.sh install-sw-lmc-base-classes
./play-task.sh install-sw-skabase
./play-task.sh install-sw-refelt
```
or using ansible-playbook directly
```
ansible-playbook -i hosts site.yml --limit local --tags "install-sw" # all
ansible-playbook -i hosts site.yml --limit local --tags "install-sw-lmc-base-classes"
ansible-playbook -i hosts site.yml --limit local --tags "install-sw-skabase"
ansible-playbook -i hosts site.yml --limit local --tags "install-sw-refelt"
```

### To regenerate POGO output
When XMI has been changed
```
cd ~/src/lmc-base-classes
purge_xmi_tree.py --path .
cd ~/src/lmc-base-classes/ansible
./play-task.sh deregister_refelts.yml
./play-task.sh generate-sw
./play-task.sh install-sw
```

### To configure a specific RefEltX TANGO facility and start its device servers (my_refelt)
You need to add the group to lmc-base-classes/ansible/hosts e.g.
```
[devXX]
devXXlmc
```

And group vars for the group in ansible/group_vars/devXX:
```
- ## Element personality
- element_details:
    type: refelt
    name: refXXX
    id: refX
```

and ansible/host_vars/devXXlmc for each host in the group as appropriate, at least:
```
ansible_ssh_host: lmc.devXX.domain
```

Lastly, you need to create an inventory for devXX in ansible/inventories/devXX defining the refX element.
Note: this may later be templated for RefElts (as it may be a useful pattern for DSH)

(If need be, deregister previous registrations with:)
```
ansible-playbook deregister_refelts.yml
```


Then do
```
ansible-playbook register-my-refelt devXX
```
this produces the ansible command line (note the --limit):
```
ansible-playbook -i hosts site.yml --limit devXX --tags register-my-refelt --verbose --ask-become-pass
```

# NOTES:

### Note 1: Role tags
Each role is included in site.yml with a tag which is the same as the role name, but using dashes
    e.g. {roles: "deploy_sw", tags: "deploy-sw"}
To execute the _full_ role use the role tag defined in site.yml
    e.g. --tags deploy-sw

Current ROLE tags:
    deploy-tangobox, deploy-sw, refresh-sw, install-sw, register-refelt
    Translating to TASK tags:
    deploy-tangobox-xxx, deploy-sw-xxx, refresh-sw-xxx, install-sw-xxx



### Note 2: Task tags:
Each task within a role is tagged with a tagname that starts with the same
role-tag defined in in roles/xxx/tasks/main.yml followed by a task specialisation
(separated with dashes)
E.g. any tag starting with deploy-sw will be found in the deploy_sw.yml role
```
    tags:
       - deploy-sw-lmc-base-classes
```
To execute a specific task specify the full --tags from the task file e.g.
```
     --tags deploy-sw-lmc-base-classes
```
Format is "<role-tag>-<task-id>" e.g. install-sw-refelt
```
    "{}-{}".format(role_tag,task_id).replace("_","-").lower()
```

### Current TASK tags:
To list the current task tags:
```
./play-task.sh

tango-cs@95f06d131e41:~/src/lmc-base-classes/ansible$ ./play-task.sh
You have to specify a roletag, and optional task-id

---------------------------<<<< ANSIBLE COMMAND LINE >>>>--------------------------------------------
echo The available task tags are:; ansible-playbook -i hosts site.yml --list-tags
-----------------------------------------------------------------------------------------------------

The available task tags are:

playbook: site.yml

  play #1 (operational): deploy_sw	TAGS: []
      TASK TAGS: [deploy-sw, deploy-sw-lmc-base-classes]

  play #2 (operational): deploy_tangobox	TAGS: []
      TASK TAGS: [debs, deploy-box-tango-java, deploy-tangobox, deploy-tangobox-debs, deploy-tangobox-itango, deploy-tangobox-mysql, deploy-tangobox-mysql-installed, deploy-tangobox-pip, deploy-tangobox-start-tango, deploy-tangobox-tango-core, deploy-tangobox-tango-java, deploy-tangobox-tango-java-pogo, deploy-tangobox-tango-webapp, itango, mysql, pip, tango-core, tango-java]

  play #3 (operational): install_sw	TAGS: []
      TASK TAGS: [install-sw, install-sw-lmc-base-classes, install-sw-refelt, install-sw-skabase]

  play #4 (operational): refresh_sw	TAGS: []
      TASK TAGS: [refresh-sw, refresh-sw-lmc-base-classes]

  play #5 (operational): register_my_refelt	TAGS: []
      TASK TAGS: [register-my-refelt, register-myrefelt-in-astor, register-myrefelt-in-astor-ds-path, register-myrefelt-in-tangodb]

  play #6 (operational): generate_sw	TAGS: []
      TASK TAGS: [generate-sw, generate-sw-refelt, generate-sw-refelt-simlib, generate-sw-skabase]

```
