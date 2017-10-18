#!/bin/bash

# e.g. ./play-task.sh role-tag[-task-id] # for local
#      ./play-task.sh role-tag[-task-id] hosts-limit
if [ -z $1 ]; then
  echo "You have to specify a role-tag[-task-id] [hosts-limit]"
  cmd="echo The available task tags are:; ansible-playbook -i hosts site.yml --list-tags"
else
  if [ -z $2 ]; then
    # No hosts-limit specified - assume local
    hosts_limit="local"
  else
    hosts_limit="$2"
  fi
  # Replace underscores with dashes for role-tag[-task-id]
  roletask=${1//[_]/-}
  cmd="ansible-playbook -i hosts site.yml --limit $hosts_limit --tags $roletask --verbose --ask-become-pass"
fi

echo
echo "---------------------------<<<< ANSIBLE COMMAND LINE >>>>--------------------------------------------"
echo $cmd
echo "-----------------------------------------------------------------------------------------------------"
echo
eval $cmd
