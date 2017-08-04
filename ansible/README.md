To deploy SW repos:
ansible-playbook -i hosts deploy_sw.yml --limit local 

To refresh SW repos:
ansible-playbook -i hosts refresh_sw.yml --limit local 

