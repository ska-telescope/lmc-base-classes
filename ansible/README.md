When everything is already deployed and installed:
. play-refresh-sw.sh local levpro
. play-install-sw.sh local skabase,refelt



To deploy SW on local: # Git clone if not available, else git pull
ansible-playbook -i hosts deploy_sw.yml --limit local --tags "levpro,skabase,refelt"

To refresh SW on local: # Git pull
ansible-playbook -i hosts refresh_sw.yml --limit local --tags "levpro"
ansible-playbook -i hosts refresh_sw.yml --limit local --tags "skabase"

To install SW on local: # sudo pip install
ansible-playbook -i hosts install_sw.yml --limit local # all
ansible-playbook -i hosts install_sw.yml --limit local --tags "levpro,skabase,refelt"
ansible-playbook -i hosts install_sw.yml --limit local --tags "skabase"
ansible-playbook -i hosts install_sw.yml --limit local --tags "refelt"
