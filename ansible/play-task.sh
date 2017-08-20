#!/bin/sh

# e.g. . play-task.sh roletag taskid
if [ -z $1 ]; then
  echo "You have to specify a roletag, and optional task-id"
  cmd="echo The available task tags are:; ansible-playbook -i hosts site.yml --list-tags"
else
  if [ -z $2 ]; then
    cmd="ansible-playbook -i hosts site.yml --limit local --tags $1 --verbose"
  else
    cmd="ansible-playbook -i hosts site.yml --limit local --tags $1-$2 --verbose"
  fi
fi

echo -----------------------------------------------------------------------------------------------------
echo $cmd
echo -----------------------------------------------------------------------------------------------------
eval $cmd
