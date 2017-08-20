#!/bin/sh

# e.g. . play-task.sh roletag taskid
if [ -z $1 ]; then
  echo "You have to specify a roletag, and optional task-id"
  cmd="echo The available task tags are:; ansible-playbook -i hosts site.yml --list-tags"
else
  if [ -z $2 ]; then
    # No taskids, so this has to be a role - replace dashes with underscores
    roletag=${1//[-]/_}
    cmd="ansible-playbook -i hosts site.yml --limit local --tags $roletag --verbose"
  else
    # Both roletag and taskids - replace underscores with dahses
    roletag=${1//[_]/-}
    taskid=${2//[_]/-}
    cmd="ansible-playbook -i hosts site.yml --limit local --tags $roletag-$taskid --verbose"
  fi
fi

echo -----------------------------------------------------------------------------------------------------
echo $cmd
echo -----------------------------------------------------------------------------------------------------
eval $cmd
