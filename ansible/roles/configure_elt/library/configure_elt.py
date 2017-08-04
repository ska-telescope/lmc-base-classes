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
	import subprocess
	import string
	import time
	import signal
	from threading import Thread

	## COMMAND-LINE ARG MODULES
	import getopt
	import argparse
	import collections

	## LOGGING MODULES
	import logging

	## XML PARSING
	import xml.etree.ElementTree as ET
	import lxml
	from lxml import etree
	from lxml import objectify

	## TANGO MODULES
	import tango
	import PyTango

except ImportError, e:
	print "failed=True msg='failed to import python module: %s'" % e
	sys.exit(1)
##################################################


#### CLASS EXECUTE PROCESS ####
class ProcessExecutor:

	""" Class to execute a process"""    
	def __init__(self, processDef):
		self.processDef = processDef
		self.t= None

	def start(self):
		try:
			self.proc = subprocess.Popen( self.processDef, 
																		shell=True,
																		stdin=subprocess.PIPE,
																		stdout=subprocess.PIPE,
																		stderr=subprocess.STDOUT)
		except:
			#logging.error('Exception occurred while defining process %s to be executed!',self.processDef)
			raise
   
		self.__sysout('[ctl] Started ' + self.processDef + '\n')

		try:
			self.t = Thread(target=self.consumeOutput)
			self.t.start()
			#while self.t.isAlive(): 
			#	self.t.join(1)
		except (KeyboardInterrupt, SystemExit):
			#logging.info('Received keyboard interrupt, quitting threads...')
			sys.exit()

		return 0

	def consumeOutput(self):
		proc = self.proc
		while True:
			line = proc.stdout.readline()
			if not line:
				break
			#self.__sysout(line)
		#self.__sysout('[ctl] Terminated\n')

	def __sysout(self, line):
		sys.stdout.write('procex[%d]: %s' % (self.proc.pid, line))


### CLASS SERVERS
class ServerInfo :
	def __init__ (self,server_name,server_instance):
		self.name = server_name
		self.instance = server_instance
		self.devices = []
	def add_device(self,device_name):	
		self.devices.append(device_name)

### COMVERT DATA ####
def convert(data):
	if isinstance(data, basestring):
		return str(data)
	elif isinstance(data, collections.Mapping):
		return dict(map(convert, data.iteritems()))
	elif isinstance(data, collections.Iterable):
		return type(data)(map(convert, data))
	else:
		return data


#### CHECK SECTION ####
def is_section(config_section):
	""" Check that given config element is a section"""
	try:
		config_section.keys()
	except AttributeError:
		return False
	return True


## VALIDATE XML CONFIG AGAINST SCHEMA
def parse_xml_config(xml_filename,schema_filename) :
	""" Validate xml config file """
	 	
	## Clear any previous errors
	lxml.etree.clear_error_log()

	# Parse string of XML
	try:		
		xml_doc = lxml.etree.parse(xml_filename)
	
	except lxml.etree.XMLSyntaxError, xse:
		# XML not well formed
		raise
  
	# Validate XML against schema?	  	
	if schema_filename :
		
		try:
			# Get the XML schema to validate against
			schema = lxml.etree.XMLSchema(file = schema_filename)
			# Validate parsed XML against schema returning a readable message on failure
			schema.assertValid(xml_doc)
			# Validate parsed XML against schema returning boolean value indicating success/failure
			
		except lxml.etree.XMLSchemaParseError, xspe:
			# Something wrong with the schema (getting from URL/parsing)
			raise

		except lxml.etree.XMLSyntaxError, xse:
			# XML not well formed
			raise
    
		except lxml.etree.DocumentInvalid, di:
			# XML failed to validate against schema
			raise

		error = schema.error_log.last_error
		if error:
			# All the error properties (from libxml2) describing what went wrong
			return None

	return xml_doc



#### FIND TANGO SERVER IN DB ####
def has_server(db,server_full_name):
	""" Check if server is present in DB """
	#logger= logging.getLogger(__name__)

	## Find server is DB
	hasServer= False
	try :
		matched_server_name= db.get_server_list(server_full_name).value_string
		if matched_server_name :
			hasServer= True	 		
	except PyTango.DevFailed as df:
		print(str(df))
		return False

	return hasServer

#### FIND TANGO DEVICE IN DB ####
def has_device(db,server_name,class_name,dev_name):
	""" Check is given device is already registered in DB """
	#logger= logging.getLogger(__name__)

	hasDevice= False

	## Find device in DB
	try :
		dev_info= db.get_device_info(dev_name)
	except PyTango.DevFailed as df:
		#logging.info("Device %s not present in TangoDB...",dev_name)
		return False

	## If it is found check that dev info corresponds to
	## class & server names
	#logger.debug("class_name: %s ",dev_info.class_name)	
	#logger.debug("ds_full_name: %s ",dev_info.ds_full_name)	
	if class_name==dev_info.class_name and server_name==dev_info.ds_full_name :
		hasDevice= True

	return hasDevice

#### REGISTER DEVICE ####
def register_device(db,server_name,class_name,dev_name,dev_alias):
	""" Register a device in DB """
	
	## Create a DevInfo
	dev_info = PyTango.DbDevInfo()
	dev_info.name = dev_name
	dev_info._class = class_name
	dev_info.server = server_name

	## Add device to DB
	try:
		db.add_device(dev_info)
	except PyTango.DevFailed as df:
		raise
			
	## Register alias
	if dev_alias:	
		try:
			## Delete alias first in DB (if alias exist put_device_alias throws an exception)
			db.delete_device_alias(dev_alias)

			## Set alias in DB
			db.put_device_alias(dev_name,dev_alias)
		except PyTango.DevFailed as df:
			raise

	return 0


### INIT DEVICE PROPERTIES ###
def init_device_properties(db,dev_name,props):
	""" Init given properties in device """

	## Check if property list is empty
	if not props:
		#logging.warn("Empty property list given, nothing to be done!")
		return 0
	#print(props)
	
	## Get properties present in device
	try:
		dev_prop_data= db.get_device_property_list(dev_name,'*')
	except PyTango.DevFailed as df:
		#logging.error("Failed to get property list of device %s!",dev_name)
		return 1

	## Check if device has properties
	dev_props= dev_prop_data.value_string
	#if not dev_props:
	#	logging.info("Device has no property defined yet...")
	
	## Loop over input properties 
	for prop in props:
		## Get prop name
		try:
			prop_name= prop['name']
			prop_value= prop['value']
		except KeyError:
			#logging.error("Failed to get keys from device property!")
			return 1
		#logging.debug("Initializing dev property %s with value %s ...",prop_name,prop_value)

		## Set property value in DB
		try:
			d = dict([(prop_name, prop_value)])
			db.put_device_property(dev_name, {prop_name:prop_value} )	
		except PyTango.DevFailed as df:
			#logging.error("Failed to put property %s to DB!",prop_name)
			return 1

	return 0


### CONFIGURE DEVICE PROPERTIES ###
def configure_device_properties(db,device_configuration_node,device_full_name):
	""" Configure given properties in device """

	logging.info("Configure given properties in device ")				

	## Get device properties
	device_properties_node= device_configuration_node.find('./DeviceProperties')
	if device_properties_node is None :
		logging.warn("Cannot find 'DeviceProperties' node in configuration file...nothing to be configured!")
		return

	## Iterate over device properties and create dictionary
	device_properties = []
					
	for dev_prop_node in device_properties_node.findall('DeviceProperty') :
		## Get prop name
		if 'name' not in dev_prop_node.attrib :
			errMsg= "Cannot find 'name' attr in device_property element!"
			logging.error(errMsg)
			raise Exception(errMsg)

		dev_prop_name= dev_prop_node.attrib.get('name').strip()

		## Get prop value(s)
		device_property_dict = {}
		device_property_dict['name']= dev_prop_name
		nvalues= len(dev_prop_node.xpath(".//Value"))
		
		if nvalues==1 :
			dev_prop_value_node= dev_prop_node.find('./Value')
			dev_prop_value_node.text = dev_prop_value_node.text.strip()
			if dev_prop_value_node.tail is not None :
				dev_prop_value_node.tail = dev_prop_value_node.tail.strip()
			dev_prop_value= dev_prop_value_node.text
			device_prop_values= dev_prop_value
		else:
			device_prop_values= []
			for dev_prop_value_node in dev_prop_node.findall('./Value') :
				dev_prop_value_node.text = dev_prop_value_node.text.strip()
				if dev_prop_value_node.tail is not None :
					dev_prop_value_node.tail = dev_prop_value_node.tail.strip()
				dev_prop_value= dev_prop_value_node.text
				device_prop_values.append(dev_prop_value)
				logging.info("Processing dev prop %s : value %s",dev_prop_name,str(dev_prop_value))					

			if not device_prop_values :
				errMsg= "Empty list of property values!"
				#logging.error(errMsg)
				raise Exception(errMsg)
					
		#logging.info("Processing dev prop %s : value %s",dev_prop_name,str(dev_prop_value))	
			
		## Fill dev prop value key	
		device_property_dict['value']= device_prop_values 
				
		## Append dictionary to list
		device_properties.append(device_property_dict)
						
	## Initialize property values
	if device_properties :
		if init_device_properties(db,device_full_name,convert(device_properties)) != 0 :
			errMsg= "Failed to initialize dev properties of device " + device_full_name + "!" 
			raise Exception(errMsg)
	else:
		errMsg= "Empty device property list detected, check!"
		raise Exception(errMsg)



### CONFIGURE DEVICE ATTRIBUTES ###
def configure_device_attributes(db,device_configuration_node,device_full_name):
	""" Configure given properties in device """

	logging.info("Configure device attributes")				

	## Get device attributes
	device_attributes_node= device_configuration_node.find('./Attributes')
	if device_attributes_node is None :
		logging.warn("Cannot find 'Attributes' node in configuration file...nothing to be configured!")
		return

	## Configure fwd attributes	
	try:
		configure_fwd_attrs(db,device_attributes_node,device_full_name)
	except:
		raise

	## Configure standard attrs?


### CONFIGURE FWD ATTRS ###
def configure_fwd_attrs(db,attr_list_node,device_full_name):
	""" Configure fwd attributes in device """

	logging.info("Configure fwd attrs in device ")				

	## Check given  node
	if attr_list_node is None :
		errMsg= "Attribute list not is null!"
		logging.error(errMsg)
		raise Exception(errMsg)

	## Iterate over fwd attr and create dictionary
					
	for fwd_attr_node in attr_list_node.findall('StaticFwdAttribute') :
		## Get prop name
		if 'name' not in fwd_attr_node.attrib :
			errMsg= "Cannot find 'name' attr in fwd attr element!"
			logging.error(errMsg)
			raise Exception(errMsg)

		fwd_attr_name= fwd_attr_node.attrib.get('name').strip()
		
		## Get prop value(s)
		# - Label
		fwd_attr_label_prop_node= fwd_attr_node.find('./Label')
		fwd_attr_label_prop_node.text = fwd_attr_label_prop_node.text.strip()
		if fwd_attr_label_prop_node.tail is not None :
			fwd_attr_label_prop_node.tail = fwd_attr_label_prop_node.tail.strip()
		fwd_attr_label= fwd_attr_label_prop_node.text

		# - Url
		fwd_attr_url_prop_node= fwd_attr_node.find('./Url')
		fwd_attr_url_prop_node.text = fwd_attr_url_prop_node.text.strip()
		if fwd_attr_url_prop_node.tail is not None :
			fwd_attr_url_prop_node.tail = fwd_attr_url_prop_node.tail.strip()
		fwd_attr_url= fwd_attr_url_prop_node.text

		logging.info("Fwd attr %s (label=%s. url=%s)",fwd_attr_name,fwd_attr_label,fwd_attr_url)

		# - Set __root_att property in DB
		fwd_attr_db_prop= db.get_device_attribute_property(device_full_name,fwd_attr_name)
		print fwd_attr_db_prop

		fwd_attr_db_prop[fwd_attr_name]['__root_att']= fwd_attr_url
		try:
			db.put_device_attribute_property(device_full_name,fwd_attr_db_prop)
		except PyTango.DevFailed as df:
			print(str(df))
			errMsg= "Failed to set __root_att property in device!"
			logging.error(errMsg)
			raise Exception(errMsg)


#### INIT DEVICES FROM XML ####
def init_dev_from_xml_config(db,tree,clear_servers):
	""" Loop over xml config and initialize devices """

	registered_servers= []

	## Traverse the XML document
	for cs_node in tree.iter('ControlSystem'):
    
		## Get domain name
		domain_name_node = cs_node.find('./domain_name')
		if domain_name_node is None :
			errMsg= "Cannot find 'domain_name' in configuration file (missing?)!"
			#logging.error(errMsg)
			raise Exception(errMsg)

		domain_name_node.text = domain_name_node.text.strip()
		if domain_name_node.tail is not None :
			domain_name_node.tail = domain_name_node.tail.strip()
		domain_name= domain_name_node.text
		if domain_name is '' :
			errMsg= "Empty domain name found in config file (check config)!"
			#logging.error(errMsg)
			raise Exception(errMsg)

		#logging.info("Domain name: %s",str(domain_name))

		## Get host name
		host_name_node = cs_node.find('./host_name')
		if host_name_node is None :
			errMsg= "Cannot find 'host_name' in configuration file (missing?)!"
			#logging.error(errMsg)
			raise Exception(errMsg)

		host_name_node.text = host_name_node.text.strip()
		if host_name_node.tail is not None :
			host_name_node.tail = host_name_node.tail.strip()
		host_name= host_name_node.text
		if host_name is '' :
			errMsg= "Empty host name found in config file (check config)!"
			#logging.error(errMsg)
			raise Exception(errMsg)

		#logging.info("Host name: %s",str(host_name))

		## Get device servers
		servers_node= cs_node.find('./device_servers')
		if servers_node is None :
			errMsg= "Cannot find 'device_servers' in configuration file (missing?)!"
			#logging.error(errMsg)
			raise Exception(errMsg)
			
		## Iterate over device servers found
		for server_node in servers_node.iter('server'):

			## Get server name & instance 
			if 'name' not in server_node.attrib or 'instance' not in server_node.attrib:
				errMsg= "Cannot find 'name' and/or 'instance' attr in server element!"
				#logging.error(errMsg)
				raise Exception(errMsg)
				
			server_name= server_node.attrib.get('name').strip()		
			server_id= server_node.attrib.get('instance').strip()
			server_full_name= server_name + "/" + server_id
			server_info= ServerInfo(server_name,server_id)

			## Get server info (optional)
			if 'startup_level' in server_node.attrib :
				startup_level= server_node.attrib.get('startup_level')
			else :
				startup_level= 1

			if 'astor_controlled' in server_node.attrib :
				astor_controlled= server_node.attrib.get('astor_controlled')	
			else :
				astor_controlled= 0

			#logging.debug("Server info: Host=%s, StartupLevel=%d, AstorControlled=%s",str(host_name),str(startup_level),str(astor_controlled))

			## Check if server is already present
			if has_server(db,server_full_name):
				#logging.info('Server %s is already present in TangoDB',server_full_name)
				if clear_servers:
					#logging.info('Deleting server %s from TangoDB',server_full_name)
					try:
						db.delete_server(server_full_name)
					except PyTango.DevFailed as df:
						#logging.error("Failed to delete server %s from DB!",server_full_name)
						raise

			#logging.info("Configuring device server %s [instance %s]",server_name,server_id)

			## Iterate over classes
			for class_node in server_node.iter('class'):
				## Get class name 
				if 'name' not in class_node.attrib :
					errMsg= "Cannot find 'name' attr in class element!"
					#logging.error(errMsg)
					raise Exception(errMsg)
									
				class_name= class_node.attrib.get('name').strip()

				## Iterate over devices
				for device_node in class_node.iter('device'):
					## Get device domain name (if not present use main domain property) 
					if 'domain' not in device_node.attrib :
						#logging.debug("No 'domain' attr present in class element, using main domain name property...")
						device_domain= domain_name
					else :
						device_domain= device_node.attrib.get('domain').strip()	

					## Get device name 
					if 'name' not in device_node.attrib :
						errMsg= "Cannot find 'name' attr in class element!"
						#logging.error(errMsg)
						raise Exception(errMsg)

					device_name= device_node.attrib.get('name').strip()
					
					## Get device family name 
					if 'family' not in device_node.attrib :
						errMsg= "Cannot find 'family' attr in class element!"
						#logging.error(errMsg)
						raise Exception(errMsg)

					device_family= device_node.attrib.get('family').strip()

					## Get device alias
					if 'alias' in device_node.attrib and device_node.attrib.get('alias') is not '':
						has_device_alias= True
						device_alias= device_node.attrib.get('alias').strip()
					else :
						has_device_alias= False
						device_alias= ''

					device_full_name= device_domain + str('/') + device_family + str('/') + device_name
					server_info.add_device(device_full_name)
					#logging.info("Registering device server %s [instance %s, class %s]: device_full_name=%s [alias=%s]",server_name,server_id,class_name,device_full_name,device_alias)

					## Check if device is already registered in DB
					hasDevice= has_device(db,server_full_name,class_name,device_full_name)
					
					try:
						register_device(db,server_full_name,class_name,device_full_name,device_alias)
					except PyTango.DevFailed as df:
						errMsg= "Failed to registed device " + device_full_name + " in DB (err=" + str(df) + ")"
						raise Exception(errMsg)
						
					## Get device configuration node
					device_configuration_node= device_node.find('./DeviceConfiguration')
					if device_configuration_node is None :
						errMsg= "Cannot find 'DeviceConfiguration' node in configuration file (missing?)!"
						#logging.error(errMsg)
						raise Exception(errMsg)
		
					## Configure device properties
					try:
						configure_device_properties(db,device_configuration_node,device_full_name)
					except:					
						raise

					## Configure device attributes
					try:
						configure_device_attributes(db,device_configuration_node,device_full_name)	
					except:					
						raise

					## Get device configuration node
					#device_configuration_node= device_node.find('./DeviceConfiguration')
					#if device_configuration_node is None :
						#errMsg= "Cannot find 'DeviceConfiguration' node in configuration file (missing?)!"
						#raise Exception(errMsg)

					## Get device properties
					#device_properties_node= device_configuration_node.find('./DeviceProperties')
					#if device_properties_node is None :
						#continue

					## Iterate over device properties and create dictionary
					#device_properties = []
					
					#for dev_prop_node in device_properties_node.findall('DeviceProperty') :
						## Get prop name
						#if 'name' not in dev_prop_node.attrib :
							#errMsg= "Cannot find 'name' attr in device_property element!"
							#raise Exception(errMsg)

						#dev_prop_name= dev_prop_node.attrib.get('name').strip()

						## Get prop value(s)
						#device_property_dict = {}
						#device_property_dict['name']= dev_prop_name
						#nvalues= len(dev_prop_node.xpath(".//Value"))
						#if nvalues==1 :
							#dev_prop_value_node= dev_prop_node.find('./Value')
							#dev_prop_value_node.text = dev_prop_value_node.text.strip()
							#if dev_prop_value_node.tail is not None :
								#dev_prop_value_node.tail = dev_prop_value_node.tail.strip()
							#dev_prop_value= dev_prop_value_node.text
							#device_prop_values= dev_prop_value
						#else :
							#device_prop_values= []
							#for dev_prop_value_node in dev_prop_node.findall('./Value') :
								#dev_prop_value_node.text = dev_prop_value_node.text.strip()
								#if dev_prop_value_node.tail is not None :
									#dev_prop_value_node.tail = dev_prop_value_node.tail.strip()
								#dev_prop_value= dev_prop_value_node.text
								#device_prop_values.append(dev_prop_value)
								
							#if not device_prop_values :
								#errMsg= "Empty list of property values!"
								#raise Exception(errMsg)
								
						## Fill dev prop value key	
						#device_property_dict['value']= device_prop_values 
				
						## Append dictionary to list
						#device_properties.append(device_property_dict)
						
					## End loop device properties						
					#print(device_properties)

					#if device_properties :
						#if init_device_properties(db,device_full_name,convert(device_properties)) != 0 :
							#errMsg= "Failed to initialize dev properties of device " + device_full_name + "!" 
							#raise Exception(errMsg)
					#else :
						#errMsg= "Empty device property list detected, check!"
						#raise Exception(errMsg)

			## Put server info in DB (startup level, etc)
			serv_info= PyTango.DbServerInfo()
			serv_info.name= str(server_full_name)
			serv_info.host= str(host_name)
			serv_info.mode= int(astor_controlled=='true')
			serv_info.level= int(startup_level)
			try :
				db.put_server_info(serv_info)
			except PyTango.DevFailed as df:
				print(str(df))
				errMsg= "Failed to put server info in TangoDB (TangoDB off or invalid syntax?)!"
				#logging.error(errMsg)
				raise Exception(errMsg)

			## If registration is completed with success add server_info to list
			registered_servers.append(server_info)

	#logging.info("End config file processing")

	return registered_servers



### EXPORT REGISTERED SERVERS ###
def export_servers(db,registered_servers):
	""" Export the registered servers """

	# Check list of given servers
	if not registered_servers:
		errMsg= "Given list of registered servers is empty!"
		#logging.error(errMsg)
		raise Exception(errMsg)

	# Iterate over servers and export one by one
	server_verbosity= 1
	final_state= tango._tango.DevState.INIT
	startup_timeout= 10 # in seconds
	sleep_time= 2 # in seconds

	for server_info in registered_servers:

		# Get server info
		server_name= server_info.name
		server_instance= server_info.instance
		devices= server_info.devices
		server_full_name= server_name + '/' + server_instance
		#logging.info("Trying to export server %s (#%s devices)",server_full_name,str(len(devices)) )

		## Start the server process
		try: 
			start_server_process(db,server_name,server_instance,server_verbosity)
		except Exception as ex:
			errMsg= "Failed to start server " + server_name + " (err= " + str(ex) + ")"
			#logging.error(errMsg)
			raise Exception(errMsg)
			
	

### START DEVICE SERVER PROCESS ###
def start_server_process(db,server_name,server_instance,verbosity):

	""" Start a device server process"""	      

	# Check device install dir environment variable 
	install_env_var= 'DSHLMC_DEVICE_DIR'
	try :
		dev_install_dir= os.environ[install_env_var]	
	except KeyError :
		#logging.error("Cannot get value of env variable %s (check given variable name) where devices are installed!",install_env_var)
		return -1

	# Set cmd name & args
	server_full_name= server_name + '/' + server_instance 
	cmd_args = ' %s -v%s' % (server_instance, verbosity)
	cmd = dev_install_dir + '/' + server_name + cmd_args
	#logging.info("Starting server %s (cmd=%s)",server_name,cmd)	

	# Run the command in a different thread	
	try:
		pe = ProcessExecutor(cmd)
		pe.start()
	except Exception as ex :
		errMsg= "Failed to start device server " + server_name + " (err=" + str(ex) + ")"
		#logging.error(errMsg)
		raise Exception(errMsg)

	## Wait until device server has completed startup (e.g. they should be in ON State)
	final_state= tango._tango.DevState.INIT
	startup_timeout= 10 # in seconds
	sleep_time= 2 # in seconds
	#logging.info("Sleeping a bit...")	
	time.sleep(sleep_time)

	try:
		startup_reached_status= wait_server_startup(db,server_full_name,final_state,startup_timeout,sleep_time)
	except Exception as ex:
		errMsg= "Failure occurred while starting server " + server_full_name + " (err=" + str(ex) + ")"
		#logging.error(errMsg)
		raise Exception(errMsg)

	if startup_reached_status !=0 :
		errMsg= "Server " +  server_full_name + " did not startup within the assumed timeout!"
		#logging.error(errMsg)
		raise Exception(errMsg)

	## Joining device server thread?
	#while pe.t.isAlive(): 
	#	pe.t.join(1)


### WAIT FOR DEVICE SERVER PROCESS TO COMPLETE STARTUP ###
def wait_server_startup(db,full_server_name,final_state,timeout,sleep_time):

	""" Wait for device server to complete the startup """
	status= 0

	## Get all devices registered in this server 
	try:
		devices_in_server= db.get_device_class_list(full_server_name)
	except PyTango.DevFailed as df:
		print(str(df))
		errMsg= "Failed to get list of devices present in server " + full_server_name
		#logging.error(errMsg)
		raise Exception(errMsg)

	device_names= []
	for item in xrange(0,devices_in_server.size()-1,2) :
		device_name= devices_in_server[item]
		class_name= devices_in_server[item+1]
		if class_name=='DServer':
			continue
		device_names.append(device_name)

	## Check if devices have started	
	for device_name in device_names:
		#logging.debug("Checking if device %s is started...", device_name)

		## Start timeout
		timeout_start = time.time()
		device_proxy= None
		device_started= False
		attempts= 0

		while time.time() < timeout_start + timeout:
			attempts+= 1

			#logging.info("Attempt #%s to check device %s startup...",str(attempts),device_name)

			## Create proxy to device 
			## NB: If fails sleep and retry later
			if device_proxy is None:
				#logging.info("Creating proxy to device %s ...",device_name)
				try:
					device_proxy= PyTango.DeviceProxy(device_name)			

				except PyTango.DevFailed as df:
					print(str(df))
					#logging.debug("Failed to create proxy to device %s, will sleep a bit and retry later...",device_name)
					time.sleep(sleep_time)
					continue

			## Get device process PID
			#logging.info("Retrieving PID of device %s ...",device_name)
			try:	
				pid= db.get_device_info(device_name).pid
			except PyTango.DevFailed as df:
				print(str(df))
				#logging.debug("Failed to get PID for device %s, will sleep a bit and retry later...",device_name)
				time.sleep(sleep_time)
				continue

			## Get device state and check if final state is reached
			if device_proxy is not None:
				#logging.info("Retrieving State of device %s ...",device_name)
				try:
					state = device_proxy.state()

					#logging.info("Device %s has reached desired state, exit loop..",device_name)
					device_started= True
					break
					#if state==tango._tango.DevState.INIT or state==tango._tango.DevState.ON or state==tango._tango.DevState.RUNNING:
					#	logging.info("Device %s has reached desired state, exit loop..",device_name)
					#	device_started= True
					#	break

				except PyTango.DevFailed as df:
					#logging.debug("Failed to get device %s State info, will sleep a bit and retry later...",device_name)
					time.sleep(sleep_time)
					continue

			time.sleep(sleep_time)
		
		## Check if this device was started
		if not device_started:
			#logging.error("Device %s in server %s did not start within the timeout (%s s)!",device_name,full_server_name,str(timeout))
			status= 1
			break

		## Kill server at the end
		#if device_proxy is not None:	
		#	logging.info("Killing device %s [adm dev=%s]",device_name,device_proxy.adm_name())
		#	admin_device= PyTango.DeviceProxy(device_proxy.adm_name())
		#	admin_device.Kill()

	## Kill OS process at the end
	if pid != 0:
		#logging.info("Killing process %s for server %s",pid,full_server_name)
		try:
			os.kill(pid, signal.SIGTERM)  #o r signal.SIGKILL
			#logging.info("Killed process PID %s for server %s",pid,full_server_name)
		except Exception as ex:
			raise
			#logging.warn("No process to be killed for server %s",full_server_name)

	return status

##################################################
###          MODULE MAIN
##################################################
def main():
	"""Main for the Ansible module"""

	## Create ansible module
	changed = False
	message = ''

	module = AnsibleModule(
		argument_spec=dict(
			inputfile=dict(required=True),
			schemafile=dict(required=False),
			loglevel=dict(required=False, default='INFO', choices=['CRITICAL','ERROR','WARN','INFO','DEBUG','OFF']),
			clear_servers=dict(required=False, type='bool', default=False, choices=BOOLEANS),
			export_servers=dict(required=False, type='bool', default=False, choices=BOOLEANS),
		),
		supports_check_mode=True
	)

	# In check mode, we take no action
	# Since this module never changes system state, we just
	# return changed=False
	if module.check_mode:
		module.exit_json(changed=False)
	
	## Get and check module args	
	filename = module.params['inputfile']
	filename_schema = module.params['schemafile']
	loglevel = module.params['loglevel']
	clear_servers = module.params['clear_servers']
	start_servers = module.params['export_servers']	
	
	if not filename:
		msg = "Empty config filename given!"
		module.fail_json(msg=msg)
		
	if filename_schema:
		has_schema= True
	else:
		has_schema= False

	## Initialize TangoDB
	try:
		db= PyTango.Database()
	except PyTango.DevFailed as df:
		msg= "Failed to get access to TangoDB (did you forget to start Tango?)!"
		module.fail_json(msg=msg)
		
	## Parse config file
	try:
		if has_schema is True:
			cfg= parse_xml_config(filename,filename_schema)
		else:
			cfg= parse_xml_config(filename,'')

	except Exception as ex:
		msg = "Exception occurred while parsing config file %s (err=%s)" % (filename,str(ex))
		module.fail_json(msg=msg)

	if cfg is None:
		msg = "Failed to open and/or parse config file %s" % filename
		module.fail_json(msg=msg)
		
	## Initialize device parsed from config file
	try: 	
		registered_servers= init_dev_from_xml_config(db,cfg,clear_servers)
	except Exception as ex:
		msg = "Tango device initialization failed with err= %s" % str(ex)
		module.fail_json(msg=msg)

	## Export registered servers
	## NB: This will startup servers and then kill it after reaching a given State
	if start_servers:
		try:
			export_servers(db,registered_servers)
		except Exception as ex:
			msg = "Failed to export registered servers (err= %s)" % str(ex)
			module.fail_json(msg=msg)

	## Always return a change?
	module.exit_json(msg="LMC configured completed with success",changed=True)
	

## Include at the end ansible (NB: it is not a standard Python include according to manual)
from ansible.module_utils.basic import *

if __name__ == '__main__':
	main()
