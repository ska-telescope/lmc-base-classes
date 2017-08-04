#!/bin/sh


ansible-playbook -i hosts refresh_sw.yml --limit local 
