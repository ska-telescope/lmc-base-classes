#!/bin/sh

# e.g. . play-install-sw.sh local tags
if [ -z $1 ]; then ansible-playbook -i hosts refresh_sw.yml --limit local
else
  if [ -z $2 ]; then ansible-playbook -i hosts refresh_sw.yml --limit $1
  else ansible-playbook -i hosts refresh_sw.yml --limit $1 --tags $2
  fi
fi
