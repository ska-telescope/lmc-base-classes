#!/usr/bin/env python

import os
import fnmatch
import argparse

from tango_simlib import sim_xmi_parser
from lxml import etree

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
                           property_type=None, purge_all=False):

    items = []
    for quality in quality_list:
        if purge_all:
            # Purge all inherited items, regardless of tracability from parent classes
            if quality_list[quality]['inherited'] == 'true':
                items.append(quality)
        else:
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
        if args.verbose:
            print "            Pruning quality_type", \
                   quality_type, qualities[quality_type]
        xmi_elements = cls.findall(quality_type)
        if args.verbose:
            print "                from xmi_elements", \
                   [elt.attrib['name'] for elt in xmi_elements]
        for xmi_element in xmi_elements:
            if xmi_element.attrib['name'] in qualities[quality_type]:
                if args.verbose:
                    print "            Deleting xmi_elements", xmi_element.attrib['name']
                cls.remove(xmi_element)


parser = argparse.ArgumentParser(description=
    "Purge inherited items that no longer have ancestors from files in tree,"
    "and when '--purge-all' is requested it will remove all inherited items")
parser.add_argument('--path', dest="path",
                    action="store",
                    required=True,
                    help="Root path of tree (mandatory)")
parser.add_argument('--files', dest="files",
                    action="store", default="*.xmi",
                    help="File name pattern to include. Default=*.xmi")
parser.add_argument('--purge-all', dest="purge_all",
                    action="store_true",
                    help="Purge all inherited elements from the file")
parser.add_argument('--verbose', dest="verbose",
                    action="store_true",
                    help="Verbose output")

args = parser.parse_args()

# Script entry point
if __name__ == '__main__':

    # Find the xmi files in the repo and store their paths
    filepaths = []
    for root, dirnames, filenames in os.walk(args.path):
        # Only process xmi files
        for filename in fnmatch.filter(filenames, "*.xmi"):
            # Append for processing if it matches the files pattern
            if fnmatch.filter([filename], args.files):
                print "Found", os.path.join(root, filename)
                filepaths.append(os.path.join(root, filename))

    for filepath in sorted(filepaths):
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
        super_classes = cls_descr.values()[0]
        # Remove the 'Device_Impl' class information
        super_class_info = [item for item in super_classes
                            if not item["classname"].startswith("Device_Impl")]
        super_class_info.reverse()

        # Create the parsers for the classes' super_classes and store in a list.
        super_class_psrs = []
        for class_info in super_class_info:
            sup_psr = sim_xmi_parser.XmiParser()
            if class_info['sourcePath'].startswith("."):
                # Handle relative path
                sup_file = os.path.join(os.path.dirname(filepath),
                                        class_info['sourcePath'],
                                        class_info['classname']+'.xmi')
            else:
                sup_file = os.path.join(class_info['sourcePath'],
                                        class_info['classname']+'.xmi')
            sup_psr.parse(sup_file)
            super_class_psrs.append(sup_psr)


        # Make use of the recursive function.
        # Create lists of features that need to be removed.
        # Gather items to delete in the attributes.
        print "    Gathering items to be removed from file..."
        qualities = {}
        qualities['attributes'] = (
            gather_items_to_delete(attr_qualities, 'device_attr',
                                   super_class_psrs,
                                   purge_all=args.purge_all))
        qualities['commands'] = (
            gather_items_to_delete(cmd_qualities, 'cmd',
                                   super_class_psrs,
                                   purge_all=args.purge_all))
        qualities['deviceProperties'] = (
            gather_items_to_delete(devprop_qualities, 'properties',
                                   super_class_psrs,
                                   property_type='deviceProperties',
                                   purge_all=args.purge_all))
        qualities['classProperties'] = (
            gather_items_to_delete(clsprop_qualities, 'properties',
                                   super_class_psrs,
                                   property_type='classProperties',
                                   purge_all=args.purge_all))

        print "    Qualities to delete in the XMI tree..."
        print "        Class Properties: ", qualities['classProperties']
        print "        Attributes: ", qualities['attributes']
        print "        Commands: ", qualities['commands']
        print "        Device Properties: ", qualities['deviceProperties']

        # Rather use lxml etree to write out the XMI files to preserve
        # the xmi_element order. The XMI file becomes somewhat difficult to read
        # if the elements are lexically sorted as done by the xmltree used inside
        # tango-simlib.
        need_to_write = 0
        for quality in ['classProperties', 'attributes',
                        'commands', 'deviceProperties']:
            need_to_write += len(qualities[quality])
        if not need_to_write:
            print "    No changes to file ", filepath
        else:
            tree = etree.parse(filepath)
            prune_xmi_tree(tree, qualities)

            # This you need to write the 'new' xmi file
            # Define the default namespace(s) before parsing the file to avoid "<ns0:PogoSystem "
            etree.register_namespace('pogoDsl', "http://www.esrf.fr/tango/pogo/PogoDsl")
            etree.register_namespace('xmi', "http://www.omg.org/XMI")
            # To write a file with the xml declaration at the top.
            print "    Overwriting file ", filepath
            tree.write(filepath, xml_declaration=True, encoding='ASCII', method='xml')
