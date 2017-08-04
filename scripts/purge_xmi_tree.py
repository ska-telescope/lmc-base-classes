#!/usr/bin/env python

import subprocess
import xml.etree.ElementTree as ET

from tango_simlib.sim_xmi_parser import XmiParser


def some_recursive_fun(quality, quality_type, the_parent_class_psr_list, some_arg=None):
    """
    """
    print quality['name']
    print "inherited: ", quality['inherited']
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


def gather_items_to_delete(quality_list, feature_type, supr_class_psrs, some_arg=None):
    some_list = []

    for quality in quality_list:
        ans = some_recursive_fun(quality_list[quality],
                                 feature_type,
                                 supr_class_psrs, some_arg)

        # Add the quality to be deleted in the appropriate list
        if ans:
            some_list.append(quality)
    return some_list


# Find the xmi files in the repo and store their paths
output = subprocess.check_output(["kat-search.py -f *.xmi"], shell=True)


# Create a list of of all the file paths.
strings = output.split("\n")
# Remove the string "DEFAULT", which is always the first output of 'kat-search.py'.
strings.remove("")
strings.remove("DEFAULTS")


for string in strings:
    # Create a parser instance for the XMI file to be pruned.
    psr = XmiParser()
    psr.parse(string)

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
    clss_descr = cls_descr.values()[0]
    # Remove the 'Device_Impl' class information
    clss_descr.pop(0)
    clss_descr.reverse()
    super_class_info = clss_descr

    # Create the parsers for the classes' super_classes and store in a list.
    super_class_psrs = []
    for class_info in super_class_info:
        sup_psr = XmiParser()
        sup_psr.parse(class_info['sourcePath']+'/'+class_info['classname']+'.xmi')
        super_class_psrs.append(sup_psr)


    # Make use of the recursive function.

    # Gather items to delete in the attributes.
    attr_list = gather_items_to_delete(attr_quality_list, 'device_attr',
                                       super_class_psrs)
    cmd_list = gather_items_to_delete(cmd_quality_list, 'cmd',
                                      super_class_psrs)
    devprop_list = gather_items_to_delete(devprop_quality_list, 'properties',
                                          super_class_psrs, some_arg='deviceProperties')
    clsprop_list = gather_items_to_delete(clsprop_quality_list, 'properties',
                                          super_class_psrs, some_arg='classProperties')


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
