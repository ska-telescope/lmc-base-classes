### When everything is already deployed and installed:
. play-refresh-sw.sh local levpro
. play-install-sw.sh local skabase,refelt



### To deploy SW on local: # Git clone if not available, else git pull
ansible-playbook -i hosts site.yml --limit local --tags "deploy_sw"

### To refresh SW on local: # Git pull
ansible-playbook -i hosts site.yml --limit local --tags "refresh_sw"
ansible-playbook -i hosts site.yml --limit local --tags "refresh-sw-levpro"
ansible-playbook -i hosts site.yml --limit local --tags "refresh-sw-tango-simlib"

### To install SW on local: # sudo pip install
ansible-playbook -i hosts site.yml --limit local --tags "install_sw" # all
ansible-playbook -i hosts site.yml --limit local --tags "install-sw-levpr"
ansible-playbook -i hosts site.yml --limit local --tags "install-sw-skabase"
ansible-playbook -i hosts site.yml --limit local --tags "install-sw-refelt"

### To get going with a fresh node:
fab proxmox.create_nodes_by_group:devl4,
ssh kat@devl4.monctl.camlab.kat.ac.za
sudo apt-get install ansible
mkdir ~/git
git clone https://github.com/larsks/ansible-toolbox ~/git/ansible-toolbox
cd ~/git/ansible-toolbox
sudo pip intall . -U
git clone https://github.com/ska-sa/levpro ~/git/levpro

### Deploy tangobox on a fresh node:
cd ~/git/levpro/ansible
ansible-playbook -i hosts site.yml --limit local --tags "deploy_tango_box"


### NOTES: 

# Note 1: Role tags
# Each role is included with a tag with underscores in site.yml
#    e.g. {roles: "deploy_sw", tags: "deploy_sw"}
# To execute the _full_ role use the --tags with the underscores
#    e.g. --tags deploy_sw


# Note 2: Task tags:
# Each task within a role is tagged with a tagname with dashes in roles/xxx/tasks/main.yml
# The tag starting with
#    e.g. tags:
#           - deploy-sw-levpro
# To execute a specific task the --tags with the dashes
#    e.g. --tags deploy-sw-levpro
# Format is "<role-tag>-<task-addition>" e.g. install-sw-refelt
#    {}-{}".format(role_tag,task_id).replace("_","-").lower()

# Current ROLE tags:
#     deploy_tangobox, deploy_sw, refresh_sw, install_sw

# Current TASK ids:
#     For deploy_tangobox: debs, tango-debs, tango-core
#     For software:        tango-simlib, levpro, skabase, refelt
# Current TASK tags:
#     [deploy-sw|refresh-sw|install-sw]-[tango-simlib|levpro|skabase|refelt]

