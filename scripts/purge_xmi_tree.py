#!/usr/bin/env python

import subprocess
import xml.etree.ElementTree as ET
from tango_simlib.sim_xmi_parser import XmiParser


def some_recursive_fun(quality, quality_type, the_parent_class_psr_list, some_arg=None):
    """
        take the quality
        check if the quality is inherited
            if not inherited
                do nothing
            else
                check quantity in parent
                    if in parent
                        do nothing
                    else
                        remove it
    """
    #print the_parent_class_psr.data_description_file_name
    print quality['name']
    print "inherited: ", quality['inherited']
    #print type(quality)
    #if len(the_parent_class_psr.get_reformatted_class_description_metadata()) == 1:
    #    return True
    #if quality['name'] in ['Status', 'State']:
    #    return
    print the_parent_class_psr_list
    if the_parent_class_psr_list == []:
        return False
    if quality['inherited'] == 'true':
        if some_arg != None:
            parent_qualities = getattr(
                the_parent_class_psr_list[0],
                'get_reformatted_{}_metadata'.format(quality_type))(some_arg)
        else:
            parent_qualities = getattr(
                the_parent_class_psr_list[0],
                'get_reformatted_{}_metadata'.format(quality_type))()
        keys = parent_qualities.keys()
        if quality['name'] in keys:
            p_quality = parent_qualities[quality['name']]
            print p_quality['name']
            print "inherited: ", p_quality['inherited']
            return some_recursive_fun(p_quality, quality_type,
                                      the_parent_class_psr_list[1:], some_arg)
        else:
            return True
    else:
        return False



# Find the xmi files in the repo and store their paths
output = subprocess.check_output(["kat-search.py -f *.xmi"], shell=True)


# Create a list of of all the file paths.
strings = output.split("\n")
# Remove the string "DEFAULT", which is always the first output of 'kat-search.py'.
strings.remove("")
strings.remove("DEFAULTS")
#print strings


for string in strings:
    psr = XmiParser()
    psr.parse(string)

    # Check if parsed xmi file does inherit from some super class.
    #print psr.class_description
    #break

    # Create lists of features that need to be removed.
    attr_list = []
    cmd_list = []
    devprop_list = []
    clsprop_list = []

    # Get all the features of the TANGO class
    attr_quality_list = psr.get_reformatted_device_attr_metadata()
    cmd_quality_list = psr.get_reformatted_cmd_metadata()
    devprop_quality_list = psr.get_reformatted_properties_metadata('deviceProperties')
    clsprop_quality_list = psr.get_reformatted_properties_metadata('classProperties')

    # Get the closest parent class.
    cls_descr = psr.get_reformatted_class_description_metadata()
    #print cls_descr
    clss_descr = cls_descr.values()[0]
    #print clss_descr
    # Remove the 'Device_Impl' class information
    clss_descr.pop(0)
    clss_descr.reverse()
    #print clss_descr
    super_class_info = clss_descr
    #print super_class_info

    # Create the parsers for the classes' super_classes and store in a list.
    super_class_psrs = []
    for class_info in super_class_info:
        sup_psr = XmiParser()
        sup_psr.parse(class_info['sourcePath']+'/'+class_info['classname']+'.xmi')
        super_class_psrs.append(sup_psr)


    # Make use of the recursive function.

    # Gather items to delete in the attributes.
    print attr_quality_list.keys()
    for attr_quality in attr_quality_list:
        attr_ans = some_recursive_fun(attr_quality_list[attr_quality],
                                      'device_attr',
                                      super_class_psrs)

        # Add the quality to be deleted in the appropriate list
        if attr_ans:
            attr_list.append(attr_quality)

    # Gather items to delete in the class properties.
    print clsprop_quality_list.keys()
    for clsprop_quality in clsprop_quality_list:
        clsprop_ans = some_recursive_fun(clsprop_quality_list[clsprop_quality],
                                         'properties', super_class_psrs,
                                         some_arg='classProperties')

        # Add the quality to be deleted in the appropriate list
        if clsprop_ans:
            clsprop_list.append(clsprop_quality)

    # Gather items to delete in the commands.
    print cmd_quality_list.keys()
    for cmd_quality in cmd_quality_list:
        cmd_ans = some_recursive_fun(cmd_quality_list[cmd_quality], 'cmd',
                                     super_class_psrs)

        # Add the quality to be deleted in the appropriate list
        if cmd_ans:
            cmd_list.append(cmd_quality)

    # Gather items to delete in the device properties.
    print devprop_quality_list.keys()
    for devprop_quality in devprop_quality_list:
        devprop_ans = some_recursive_fun(devprop_quality_list[devprop_quality],
                                         'properties', super_class_psrs,
                                         some_arg='deviceProperties')

        # Add the quality to be deleted in the appropriate list
        if devprop_ans:
            devprop_list.append(devprop_quality)


    print "Qualities to delete in the XMI tree..."
    print "Class Properties: ", clsprop_list
    print "Attributes: ", attr_list
    print "Commands: ", cmd_list
    print "Device Properties: ", devprop_list
    break

# This you need to write the 'new' xmi file
## Define the default namespace(s) before parsing the file to avoid "<ns0:PogoSystem "
## ET.register_namespace('pogoDsl', "http://www.esrf.fr/tango/pogo/PogoDsl")
## ET.register_namespace('xmi', "http://www.omg.org/XMI")
# To write a file with the xml declaration at the top.
## tree.write('WeatherF.xmi', xml_declaration=True, encoding='ASCII', method='xml')

#data_description_file_name = strings[0]
#tree = ET.parse(strings[0])
#root = tree.getroot()
#device_class = root.find('classes')a
#device_class_name = device_class.attrib['name']

#print device_class_name
#print device_class
