#!/bin/sh

# e.g. . play-task.sh roletag taskid
if [ -z $1 ]; then cmd = "ansible-playbook -i hosts site.yml --limit local --tags $1 --verbose"
else
  if [ -z $2 ]; then cmd="ansible-playbook -i hosts site.yml --limit local --tags $1 --verbose"
  else cmd="ansible-playbook -i hosts install_sw.yml --limit local --tags $1-$2 --verbose"
  fi
fi

echo -----------------------------------------------------------------------------------------------------
echo $cmd
echo -----------------------------------------------------------------------------------------------------
eval $cmd
