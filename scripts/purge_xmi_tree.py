#!/usr/bin/env python

import os
import fnmatch

from tango_simlib import sim_xmi_parser

ET = sim_xmi_parser.ET

def is_quality_untraceable(quality, quality_type, parent_class_psrs, property_type=None):

    if parent_class_psrs == []:
        return False
    if quality['inherited'] == 'true':
        if property_type != None:
            parent_qualities = getattr(
                parent_class_psrs[0],
                'get_reformatted_{}_metadata'.format(quality_type))(property_type)
        else:
            parent_qualities = getattr(
                parent_class_psrs[0],
                'get_reformatted_{}_metadata'.format(quality_type))()
        keys = parent_qualities.keys()
        if quality['name'] in keys:
            p_quality = parent_qualities[quality['name']]
            return is_quality_untraceable(p_quality, quality_type,
                                          parent_class_psrs[1:], property_type)
        else:
            return True
    else:
        return False


def gather_items_to_delete(quality_list, quality_type, parent_class_psrs,
                           property_type=None):

    items = []
    for quality in quality_list:
        untraceable = is_quality_untraceable(quality_list[quality],
                                             quality_type,
                                             parent_class_psrs, property_type)
        # Add the quality to be deleted in the appropriate list
        if untraceable:
            items.append(quality)
    return items


def prune_xmi_tree(xmi_tree, qualities):

    cls = xmi_tree.find('classes')
    for quality_type in qualities:
        xmi_elements = cls.findall(quality_type)
        for xmi_element in xmi_elements:
            if xmi_element.attrib['name'] in qualities[quality_type]:
                cls.remove(xmi_element)

# Find the xmi files in the repo and store their paths
filepaths = []
for root, dirnames, filenames in os.walk('.'):
    for filename in fnmatch.filter(filenames, '*.xmi'):
        filepaths.append(os.path.join(root, filename))


for filepath in filepaths:
    # Create a parser instance for the XMI file to be pruned.
    print "File to prune: ", filepath
    psr = sim_xmi_parser.XmiParser()
    psr.parse(filepath)

    # Get all the features of the TANGO class
    attr_qualities = psr.get_reformatted_device_attr_metadata()
    cmd_qualities = psr.get_reformatted_cmd_metadata()
    devprop_qualities = psr.get_reformatted_properties_metadata('deviceProperties')
    clsprop_qualities = psr.get_reformatted_properties_metadata('classProperties')

    # Get the closest parent class.
    cls_descr = psr.class_description
    super_class_info = cls_descr.values()[0]
    # Remove the 'Device_Impl' class information
    super_class_info.pop(0)
    super_class_info.reverse()

    # Create the parsers for the classes' super_classes and store in a list.
    super_class_psrs = []
    for class_info in super_class_info:
        sup_psr = sim_xmi_parser.XmiParser()
        sup_psr.parse(class_info['sourcePath']+'/'+class_info['classname']+'.xmi')
        super_class_psrs.append(sup_psr)


    # Make use of the recursive function.
    # Create lists of features that need to be removed.
    # Gather items to delete in the attributes.
    print "Gathering items to be removed from file..."
    qualities = {}
    qualities['dynamicAttributes'] = (
        gather_items_to_delete(attr_qualities, 'device_attr', super_class_psrs))
    qualities['commands'] = (
        gather_items_to_delete(cmd_qualities, 'cmd', super_class_psrs))
    qualities['deviceProperties'] = (
        gather_items_to_delete(devprop_qualities, 'properties', super_class_psrs,
                               property_type='deviceProperties'))
    qualities['classProperties'] = (
        gather_items_to_delete(clsprop_qualities, 'properties', super_class_psrs,
                               property_type='classProperties'))

    print "Qualities to delete in the XMI tree..."
    print "Class Properties: ", qualities['classProperties']
    print "Attributes: ", qualities['dynamicAttributes']
    print "Commands: ", qualities['commands']
    print "Device Properties: ", qualities['deviceProperties']

    tree = psr.get_xmi_tree()
    prune_xmi_tree(tree, qualities)

    # This you need to write the 'new' xmi file
    # Define the default namespace(s) before parsing the file to avoid "<ns0:PogoSystem "
    ET.register_namespace('pogoDsl', "http://www.esrf.fr/tango/pogo/PogoDsl")
    ET.register_namespace('xmi', "http://www.omg.org/XMI")
    # To write a file with the xml declaration at the top.
    print "Overwriting file ", filepath
    tree.write(filepath, xml_declaration=True, encoding='ASCII', method='xml')
