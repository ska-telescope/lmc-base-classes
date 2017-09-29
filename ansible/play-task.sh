#!/bin/bash

# e.g. ./play-task.sh role-tag task-id or
#      ./play-task.sh role-tag-task-id or
if [ -z $1 ]; then
  echo "You have to specify a roletag, and optional task-id"
  cmd="echo The available task tags are:; ansible-playbook -i hosts site.yml --list-tags"
else
  if [ -z $2 ]; then
    # No seperate taskid, replace underscores with dashes
    roletag=${1//[_]/-}
    cmd="ansible-playbook -i hosts site.yml --limit local --tags $roletag "\
        "--verbose --ask-sudo-pass"
  else
    # Both roletag and taskid - replace underscores with dashes
    roletag=${1//[_]/-}
    taskid=${2//[_]/-}
    cmd="ansible-playbook -i hosts site.yml --limit local --tags $roletag-$taskid "\
        "--verbose --ask-sudo-pass"
  fi
fi

echo
echo "---------------------------<<<< ANSIBLE COMMAND LINE >>>>--------------------------------------------"
echo $cmd
echo "-----------------------------------------------------------------------------------------------------"
echo
eval $cmd
