# LEvPro Deployment Notes
Notes for LEvPRo deployment can be found in:
[LEvPro Deployment Notes](https://docs.google.com/document/d/12f495FEMOi0g3bJjoZL3icZaCCr7iSjTY3jToFqA2Ns/edit#)

## play-task - A utility to run a single specific task
(based on ROLE tags and TASK IDs desribed in NOTES below)

To run a full role (use the ROLE name with underscores)
```
./play-task.sh install_sw
or
./play-task.sh refresh_sw
```

To run a specific task (use ROLE tags plus TASK IDs with dashes)
```
./play-task.sh install-sw skabase
or
./play-task.sh deploy-box start-tango
```

### To deploy SW on local: # Git clone if not available, else git pull
```
./play-task.sh deploy_sw
or
ansible-playbook -i hosts site.yml --limit local --tags "deploy_sw"
```

### To refresh SW on local: # Git pull
```
./play-task.sh refresh_sw
./play-task.sh refresh-sw levpro
./play-task.sh refresh-sw tango-simlib
or
ansible-playbook -i hosts site.yml --limit local --tags "refresh_sw"
ansible-playbook -i hosts site.yml --limit local --tags "refresh-sw-levpro"
ansible-playbook -i hosts site.yml --limit local --tags "refresh-sw-tango-simlib"
```

### To install SW on local: # sudo pip install
```
./play-task.sh install_sw
./play-task.sh install-sw levpro
./play-task.sh install-sw skabase
./play-task.sh install-sw refelt
or
ansible-playbook -i hosts site.yml --limit local --tags "install_sw" # all
ansible-playbook -i hosts site.yml --limit local --tags "install-sw-levpro"
ansible-playbook -i hosts site.yml --limit local --tags "install-sw-skabase"
ansible-playbook -i hosts site.yml --limit local --tags "install-sw-refelt"
```

### To get going with a fresh node:
```
fab proxmox.create_nodes_by_group:devl4,
ssh kat@devl4.monctl.camlab.kat.ac.za
sudo apt-get install ansible
mkdir ~/git
git clone https://github.com/larsks/ansible-toolbox ~/git/ansible-toolbox
cd ~/git/ansible-toolbox
sudo pip intall . -U
git clone https://github.com/ska-sa/levpro ~/git/levpro
```

### Deploy tangobox on a fresh node:
```
cd ~/git/levpro/ansible
ansible-playbook -i hosts site.yml --limit local --tags "deploy_tangobox"

ansible-playbook -i hosts site.yml --limit local --tags "deploy_sw"
ansible-playbook -i hosts site.yml --limit local --tags "refresh_sw"
ansible-playbook -i hosts site.yml --limit local --tags "install_sw"
```

# NOTES: 

### Note 1: Role tags
Each role is included with a tag with underscores in site.yml
    e.g. {roles: "deploy_sw", tags: "deploy_sw"}
To execute the _full_ role use the --tags with the underscores
    e.g. --tags deploy_sw

Current ROLE tags:
    deploy_tangobox, deploy_sw, refresh_sw, install_sw
    Translating to TASK tags:
    deploy-box-xxx, deploy-sw-xxx, refresh-sw-xxx, install-sw-xxx



### Note 2: Task tags:
Each task within a role is tagged with a tagname with dashes in roles/xxx/tasks/main.yml
The tag starting with e.g. 
```
    tags:
       - deploy-sw-levpro
```
To execute a specific task the --tags with the dashes e.g.
```
     --tags deploy-sw-levpro
```
Format is "<role-tag>-<task-addition>" e.g. install-sw-refelt
```
    "{}-{}".format(role_tag,task_id).replace("_","-").lower()
```

### Current TASK ids:
     For deployment:      debs, tango-debs, core, pip
     For software:        tango-simlib, levpro, skabase, refelt
### Current TASK tags:
     [deploy-sw|refresh-sw|install-sw]-[tango-simlib|levpro|skabase|refelt]

