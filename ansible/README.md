# LEvPro Deployment Notes
Notes for LEvPRo deployment can be found in:
[LEvPro Deployment Notes](https://docs.google.com/document/d/12f495FEMOi0g3bJjoZL3icZaCCr7iSjTY3jToFqA2Ns/edit#)

## play-task - A utility to run a single specific task
(based on ROLE tags and TASK IDs desribed in NOTES below)

To see all task tags execute:
```
./play-task.sh
```

To run a full role (use the ROLE name with underscores)
```
./play-task.sh install-sw
or
./play-task.sh refresh-sw
```

To run a specific task (use ROLE tags plus TASK IDs with dashes)
```
./play-task.sh install-sw skabase
or
./play-task.sh install-sw-skabase
or
./play-task.sh deploy-tangobox start-tango
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

### Current TASK ids:
     For deployment:      debs, tango-debs, core, pip
     For software:        tango-simlib, levpro, skabase, refelt
### Current TASK tags:
     [deploy-sw|refresh-sw|install-sw]-[tango-simlib|levpro|skabase|refelt]
