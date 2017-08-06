#!/usr/bin/python

##################################################
###          MODULE IMPORT
##################################################
try:
  # Put any initial imports here - we can't use module.fail_json b/c we haven't
  # imported stuff from ansible.module_utils.basic yet
	#import configure_devices
	
	## STANDARD MODULES
	import os
	import sys
	import getpass
	
except ImportError, e:
	print "failed=True msg='failed to import python module: %s'" % e
	sys.exit(1)
##################################################

def get_path_subdirs(path_name):
	"""Extract path subdirs"""
	folders = []
	subdirs = [path_name]
	path= path_name
	while 1:
		path, folder = os.path.split(path)
		

		if folder != "":
			folders.append(folder)
		else:
			if path != "":
				folders.append(path)
			break
		subdirs.append(path)

	folders.reverse()
	return subdirs, folders


def find_nestest_existing_dir_in_path(path_name):
	"""Find nestest existing dir in path"""
	# Get subdirectories
	subdirs, folders= get_path_subdirs(path_name)
	
	# Iterate over subdirectories and find first
	found_existing= False
	for item in subdirs:
		if os.path.isdir(item):
			nestest_existing_path= item
			break
			
	return nestest_existing_path


def is_valid_ascii(path):
	"""Check if string is valid ascii"""
	try:	
		path.decode('ascii')
		valid= True
	except UnicodeDecodeError:
		valid= False
	return valid

##################################################
###          MODULE MAIN
##################################################
def main():
	"""Main for the Ansible module"""

	## Create ansible module
	changed = False
	message = ''
	current_user= getpass.getuser()

	module = AnsibleModule(
		argument_spec=dict(
			path=dict(required=True)
		),
		supports_check_mode=True
	)

	# In check mode, we take no action
	# Since this module never changes system state, we just
	# return changed=False
	if module.check_mode:
		module.exit_json(changed=False)
	
	## Check if arg is valid ascii
	if not is_valid_ascii(module.params['path']):
		msg= "Directory/path has non ASCII characters!"
		module.fail_json(msg=msg)
	
	## Get and check module args
	path = module.params['path']

	## Check if path is an absolute path
	if not os.path.isabs(path):
		msg= "Directory/path " + str(path) + " is not an absolute path!"
		module.fail_json(msg=msg)
	
	## Split path in all possible sub-components
	nestest_existing_dir_in_path= find_nestest_existing_dir_in_path(path)

	## Check if writable
	writable= os.access(nestest_existing_dir_in_path, os.W_OK)
	if writable:
		msg = "Nestest existing directory (" + nestest_existing_dir_in_path + ') in path ' + str(path) + " is writable for current user " + str(current_user)
		module.exit_json(msg=msg,changed=False,writable=writable)
	else:
		msg = "Nestest existing directory (" + nestest_existing_dir_in_path + ') in path ' + str(path) + " is not writable for current user " + str(current_user)
		module.exit_json(msg=msg,changed=False,writable=writable)
	

## Include at the end ansible (NB: it is not a standard Python include according to manual)
from ansible.module_utils.basic import *

if __name__ == '__main__':
	main()
