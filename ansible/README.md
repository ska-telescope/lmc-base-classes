# LEvPro Deployment Notes
Notes for LEvPRo deployment can be found in:
[LEvPro Deployment Notes](https://docs.google.com/document/d/12f495FEMOi0g3bJjoZL3icZaCCr7iSjTY3jToFqA2Ns/edit#)

## play-task - A utility to run a single specific task
(based on ROLE tags and TASK IDs desribed in NOTES below)

To see all task tags execute:
```
./play-task.sh
```

To run a full role (use the ROLE name)
```
./play-task.sh install-sw
or
./play-task.sh refresh-sw
```

To run a specific task (use ROLE tags plus TASK ID)
```
./play-task.sh install-sw-skabase
or
./play-task.sh install-sw skabase
or
./play-task.sh deploy-tangobox start-tango
```

## To run a role

To see all playbooks exposing the roles:
```
ls -la *.yml
```

To run the role, run the playbook like any of the lines below:
```
./play-task.sh install-sw
./play-task.sh refresh-sw
ansible-playbook -i hosts install_sw.yml --list-tags
ansible-playbook -i hosts install_sw.yml
ansible-playbook -i hosts install_sw.yml -t install-sw-levpro
```

### To deploy SW on local: # Git clone if not available, else git pull
```
./play-task.sh deploy-sw
or
ansible-playbook -i hosts site.yml --limit local --tags "deploy-sw"
```

### To refresh SW on local: # Git pull
```
./play-task.sh refresh-sw
./play-task.sh refresh-sw levpro
./play-task.sh refresh-sw tango-simlib
or
ansible-playbook -i hosts site.yml --limit local --tags "refresh-sw"
ansible-playbook -i hosts site.yml --limit local --tags "refresh-sw-levpro"
ansible-playbook -i hosts site.yml --limit local --tags "refresh-sw-tango-simlib"
```

### To install SW on local: # sudo pip install
```
./play-task.sh install-sw
./play-task.sh install-sw-levpro
./play-task.sh install-sw-skabase
./play-task.sh install-sw-refelt
or
ansible-playbook -i hosts site.yml --limit local --tags "install-sw" # all
ansible-playbook -i hosts site.yml --limit local --tags "install-sw-levpro"
ansible-playbook -i hosts site.yml --limit local --tags "install-sw-skabase"
ansible-playbook -i hosts site.yml --limit local --tags "install-sw-refelt"
```

### To get going with a fresh node:
```
fab proxmox.create_nodes_by_group:devl4,
ssh kat@devl4.monctl.camlab.kat.ac.za
# Add this apt repo to get recent version of ansible (>=2.3.2)
# Needed on Ubuntu 14.04, might not be required on later releases
sudo add-apt-repository ppa:ansible/ansible
sudo apt-get update
sudo apt-get install ansible
mkdir ~/git
git clone https://github.com/ska-sa/levpro ~/git/levpro
```

### Deploy tangobox on a fresh node:
```
cd ~/git/levpro/ansible
./play-task.sh deploy-tangobox
./play-task.sh deploy-sw
./play-task.sh refresh-sw
./play-task.sh install-sw
```
### To regenerate POGO output:
```
cd ~/git/levpro/ansible
./play-task.sh generate-sw
```

### To configure the RefElt TANGO facility and start its device servers.
```
./play-task.sh register-refelt-in-tangodb
./play-task.sh register-refelt-in-astor
```

### To configure any RefElt TANGO facility and start its device servers.
You need to add the group to hosts e.g.
[devl4]
devl4levpro

And define ansible/group_vars for the group:
```
- ## Element personality
- element_details:
    - type: refelt
    - name: ref
    - template: refelt_template
```

and ansible/host_vars for each host in the group as appropriate, at least:
```
ansible_ssh_host: levpro.devl4.camlab.kat.ac.za
```

Then do
```
ansible-playbook register-my-refelt.yml --extra-vars "which=devl4"
```

# NOTES:

### Note 1: Role tags
Each role is included with a tag with dashes in site.yml
    e.g. {roles: "deploy_sw", tags: "deploy-sw"}
To execute the _full_ role use the role tag defined in site.yml
    e.g. --tags deploy-sw

Current ROLE tags:
    deploy-tangobox, deploy-sw, refresh-sw, install-sw, register-refelt
    Translating to TASK tags:
    deploy-tangobox-xxx, deploy-sw-xxx, refresh-sw-xxx, install-sw-xxx



### Note 2: Task tags:
Each task within a role is tagged with a tagname that starts with the samples
role tag defined in in roles/xxx/tasks/main.yml followed by a task specialisation
(separated with dashes)
The tag starting with e.g. will be found in the deploy_sw.yml role
```
    tags:
       - deploy-sw-levpro
```
To execute a specific task specify the full --tags from the role file e.g.
```
     --tags deploy-sw-levpro
```
Format is "<role-tag>-<task-tag>" e.g. install-sw-refelt
```
    "{}-{}".format(role_tag,task_id).replace("_","-").lower()
```

### Current TASK tags:
To list the current task tags:
```
./play-task.sh 

kat@levpro.devl4.camlab.kat.ac.za:~/git/levpro/ansible$ ./play-task.sh 
You have to specify a roletag, and optional task-id

---------------------------<<<< ANSIBLE COMMAND LINE >>>>--------------------------------------------
echo The available task tags are:; ansible-playbook -i hosts site.yml --list-tags
-----------------------------------------------------------------------------------------------------

The available task tags are:

playbook: site.yml

  play #1 (local): deploy_sw	TAGS: []
      TASK TAGS: [deploy-sw, deploy-sw-levpro, deploy-sw-tango-simlib]

  play #2 (local): deploy_tangobox	TAGS: []
      TASK TAGS: [debs, deploy-box-tango-java, deploy-tangobox, deploy-tangobox-debs, deploy-tangobox-itango, deploy-tangobox-mysql, deploy-tangobox-mysql-installed, deploy-tangobox-pip, deploy-tangobox-start-tango, deploy-tangobox-tango-core, deploy-tangobox-tango-java, deploy-tangobox-tango-java-pogo, itango, mysql, pip, tango-core, tango-java]

  play #3 (local): install_sw	TAGS: []
      TASK TAGS: [install-sw, install-sw-levpro, install-sw-refelt, install-sw-skabase, install-sw-tango-simlib]

  play #4 (local): refresh_sw	TAGS: []
      TASK TAGS: [refresh-sw, refresh-sw-levpro, refresh-sw-tango-simlib]

  play #5 (local): register_refelt	TAGS: []
      TASK TAGS: [register-elt-in-astor, register-elt-in-tangodb, register-refelt, register-refelt-in-astor, register-refelt-in-astor-ds-path, register-refelt-in-tangodb]

  play #6 (local): generate_sw	TAGS: []
      TASK TAGS: [generate-sw, generate-sw-refelt, generate-sw-skabase]
```
