When everything is already deployed and installed:
. play-local-refresh.sh

To deploy SW repos on local:
ansible-playbook -i hosts deploy_sw.yml --limit local

To refresh SW repos on local:
ansible-playbook -i hosts refresh_sw.yml --limit local

To refresh SW on local:
ansible-playbook -i hosts refresh_sw.yml --limit local --tags "refersh" --tags "levpro,skabase,genelt"

To install SW on local:
ansible-playbook -i hosts refresh_sw.yml --limit local --tags "install" --tags "levpro"
ansible-playbook -i hosts refresh_sw.yml --limit local --tags "install" --tags "skabase"
ansible-playbook -i hosts refresh_sw.yml --limit local --tags "install" --tags "genelt"
