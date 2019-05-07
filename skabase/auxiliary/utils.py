"""General utilities that may be useful to SKA devices and clients."""
from builtins import str
import ast
import inspect
import json
import pydoc
import traceback
import sys

from datetime import datetime

import tango
from tango import (DeviceProxy, DbDatum, DbDevInfo, AttrQuality,
                   AttrWriteType, Except, ErrSeverity)
from tango import DevState as _DevState
from contextlib import contextmanager

from faults import GroupDefinitionsError
from faults import SKABaseError

int_types = {tango._tango.CmdArgType.DevUShort,
             tango._tango.CmdArgType.DevLong,
             tango._tango.CmdArgType.DevInt,
             tango._tango.CmdArgType.DevULong,
             tango._tango.CmdArgType.DevULong64,
             tango._tango.CmdArgType.DevLong64,
             tango._tango.CmdArgType.DevShort}

float_types = {tango._tango.CmdArgType.DevDouble,
               tango._tango.CmdArgType.DevFloat}

# TBD - investigate just using (command argin data_type)
tango_type_conversion = {tango.CmdArgType.DevUShort.real: 'int',
                         tango.CmdArgType.DevLong.real: 'int',
                         tango.CmdArgType.DevInt.real: 'int',
                         tango.CmdArgType.DevULong.real: 'int',
                         tango.CmdArgType.DevULong64.real: 'int',
                         tango.CmdArgType.DevLong64.real: 'int',
                         tango.CmdArgType.DevShort.real: 'int',
                         tango.CmdArgType.DevDouble.real: 'float',
                         tango.CmdArgType.DevFloat.real: 'float',
                         tango.CmdArgType.DevString.real: 'str',
                         tango.CmdArgType.DevBoolean.real: 'bool',
                         tango.CmdArgType.DevEncoded.real: 'encoded',
                         tango.CmdArgType.DevState.real: 'state',
                         tango.CmdArgType.DevVoid.real: 'void',
                         tango.CmdArgType.DevEnum.real: 'enum',
                         }
# TBD - not all tango types are used
# tango.CmdArgType.ConstDevString           tango.CmdArgType.DevState
# tango.CmdArgType.DevVarLong64Array        tango.CmdArgType.conjugate
# tango.CmdArgType.DevBoolean               tango.CmdArgType.DevString
# tango.CmdArgType.DevVarLongArray          tango.CmdArgType.denominator
# tango.CmdArgType.DevDouble                tango.CmdArgType.DevUChar
# tango.CmdArgType.DevVarLongStringArray    tango.CmdArgType.imag
# tango.CmdArgType.DevEncoded               tango.CmdArgType.DevULong
# tango.CmdArgType.DevVarShortArray         tango.CmdArgType.mro
# tango.CmdArgType.DevEnum                  tango.CmdArgType.DevULong64
# tango.CmdArgType.DevVarStateArray         tango.CmdArgType.name
# tango.CmdArgType.DevFloat                 tango.CmdArgType.DevUShort
# tango.CmdArgType.DevVarStringArray        tango.CmdArgType.names
# tango.CmdArgType.DevInt                   tango.CmdArgType.DevVarBooleanArray
# tango.CmdArgType.DevVarULong64Array       tango.CmdArgType.numerator
# tango.CmdArgType.DevLong                  tango.CmdArgType.DevVarCharArray
# tango.CmdArgType.DevVarULongArray         tango.CmdArgType.real
# tango.CmdArgType.DevLong64                tango.CmdArgType.DevVarDoubleArray
# tango.CmdArgType.DevVarUShortArray        tango.CmdArgType.values
# tango.CmdArgType.DevPipeBlob              tango.CmdArgType.DevVarDoubleStringArray
# tango.CmdArgType.DevVoid
# tango.CmdArgType.DevShort                 tango.CmdArgType.DevVarFloatArray


@contextmanager
def exception_manager(cls, callback=None):
    try:
        yield
    except tango.DevFailed as df:
        # Find caller from the relative point of this executing handler
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)

        # Form exception message
        message = "{}: {}".format(type(df).__name__, df.message)

        # Retrieve class
        class_name = str(cls.__class__.__name__)

        # Add info to message
        additional_info = traceback.format_exc()
        message = message + " [--" + additional_info + "--] "

        # cls.exception(command_name=class_name + "::" + calframe[2][3],
        #               command_inputs=str(arguments),
        #               message=message)
        if callback:
            callback()

        tango.Except.re_throw_exception(df, "SKA_CommandFailed", message,
                                        class_name + "::" + calframe[2][3])
    except Exception as df:
        # Find caller from the relative point of this executing handler
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)

        # Form exception message
        message = "{}: {}".format(type(df).__name__, df.message)

        # Retrieve class
        class_name = str(cls.__class__.__name__)

        # Add info to message
        additional_info = traceback.format_exc()
        message = message + " [--" + additional_info + "--] "

        #  cls.exception(command_name=class_name+"::"+calframe[2][3],
        #                command_inputs=str(arguments),
        #                message=message)

        if callback:
            callback()

        tango.Except.throw_exception("SKA_CommandFailed", message,
                                     class_name + "::" + calframe[2][3])


def get_dev_info(domain_name, device_server_name, device_ref):
    dev_info = DbDevInfo()
    dev_info._class = device_server_name
    dev_info.server = '%s/%s' % (device_server_name, domain_name)
    # add the device
    dev_info.name = '%s/%s' % (domain_name, device_ref)
    return dev_info


def dp_set_property(device_name, property_name, property_value):
    dp = DeviceProxy(device_name)
    db_datum = DbDatum()
    db_datum.name = property_name
    if isinstance(property_value, list):
        for value in property_value:
            db_datum.value_string.append(value)
    else:
        db_datum.value_string.append(property_value)
    dp.put_property(db_datum)


def get_device_group_and_id(device_name):
    device_name = device_name
    return device_name.split('/')[1:]


def convert_api_value(param_dict):
    """
    Used to validate tango command parameters which are passed via json
    :param param_dict:
    :return:
    """
    VALID_TYPES = ['int', 'bool', 'str', 'float']
    type_str = param_dict.get('type', 'str').lower()
    if type_str not in VALID_TYPES:
        raise Exception('Valid types must be from %s' % ', '.join(VALID_TYPES))

    value_type = pydoc.locate(type_str)
    if value_type == bool:
        if not param_dict.get('value').lower() in ['true', 'false']:
            raise Exception('Parameter value %s is not of type %s'
                            % (param_dict.get('value'), value_type))
        value = param_dict.get('value').lower() == 'true'
    else:
        value = value_type(param_dict.get('value'))
    return param_dict.get('name'), value


def coerce_value(value):
    # Enum is not serialised correctly as json
    # _DevState  is tango._tango.DevState
    # because DevState  is tango._tango.DevState != tango.DevState
    if type(value) in [DevState, _DevState]:
        return str(value)
    return value


def get_dp_attribute(device_proxy, attribute, with_value=False, with_context=False):
    attr_dict = {
        'name': attribute.name,
        'polling_frequency': attribute.events.per_event.period,
        'min_value': (attribute.min_value if attribute.min_value != 'Not specified'
                      else None),
        'max_value': (attribute.max_value if attribute.max_value != 'Not specified'
                      else None),
        'readonly': attribute.writable not in [AttrWriteType.READ_WRITE,
                                               AttrWriteType.WRITE,
                                               AttrWriteType.READ_WITH_WRITE]
    }

    # TBD - use tango_type_conversion dict, or just str(attribute.data_format)
    if attribute.data_format == tango._tango.AttrDataFormat.SCALAR:
        if attribute.data_type in int_types:
            attr_dict["data_type"] = "int"
        elif attribute.data_type in float_types:
            attr_dict["data_type"] = "float"
        elif attribute.data_type == tango._tango.CmdArgType.DevString:
            attr_dict["data_type"] = "str"
        elif attribute.data_type == tango._tango.CmdArgType.DevBoolean:
            attr_dict["data_type"] = "bool"
        elif attribute.data_type == tango._tango.CmdArgType.DevEncoded:
            attr_dict["data_type"] = "encoded"
        elif attribute.data_type == tango._tango.CmdArgType.DevVoid:
            attr_dict["data_type"] = "void"
    else:
        # Data types we aren't really going to represent
        attr_dict["data_type"] = "other"

    if with_context:
        device_type, device_id = get_tango_device_type_id(device_proxy.dev_name())
        attr_dict['component_type'] = device_type
        attr_dict['component_id'] = device_id

    if with_value:
        try:
            attr_value = device_proxy.read_attribute(attribute.name)
            attr_dict['value'] = coerce_value(attr_value.value)
            attr_dict['is_alarm'] = attr_value.quality == AttrQuality.ATTR_ALARM
            ts = datetime.fromtimestamp(attr_value.time.tv_sec)
            ts.replace(microsecond=attr_value.time.tv_usec)
            attr_dict['timestamp'] = ts.isoformat()
        except:
            # TBD - decide what to do - add log?
            pass

    return attr_dict


def get_dp_command(device_name, command, with_context=False):
    """
    :param command:
    :return:
    """

    def command_parameters(command_desc):
        try:
            non_json = ['', 'none', 'Uninitialised']
            if command_desc in non_json:
                return []
            # ugghhh POGO replaces quotes with backticks :(
            return ast.literal_eval(command_desc.replace('`', "'"))
        except Exception:
            # TBD - decide what to do - add log?
            pass
        return []

    command_dict = {
        'name': command.cmd_name,
        'parameters': command_parameters(command.in_type_desc)
    }

    if with_context:
        device_type, device_id = get_tango_device_type_id(device_name)
        command_dict['component_type'] = device_type
        command_dict['component_id'] = device_id

    return command_dict


def get_tango_device_type_id(tango_address):
    return tango_address.split('/')[1:3]


# JSON `load` and `loads` equivalents, that force all strings to be returned
# as byte strings, rather than unicode.  This is critical for fields that will
# be used by TANGO, as it breaks with unicode strings.
# Solution from:  https://stackoverflow.com/a/33571117

def json_load_byteified(file_handle):
    """Similar to json.load(), but forces str instead of unicode strings."""
    return _byteify(
        json.load(file_handle, object_hook=_byteify),
        ignore_dicts=True
    )


def json_loads_byteified(json_text):
    """Similar to json.loads(), but forces str instead of unicode strings."""
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )


def _byteify(data, ignore_dicts=False):
    """If this is a unicode string, return its string representation."""
    if isinstance(data, str):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [_byteify(item, ignore_dicts=True) for item in data]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.items()
        }
    # if it's anything else, return it in its original form
    return data


def get_groups_from_json(json_definitions):
    """Return a dict of tango.Group objects matching the JSON definitions.

    Extracts the definitions of groups of devices and builds up matching
    tango.Group objects.  Some minimal validation is done - if the definition
    contains nothing then None is returned, otherwise an exception will
    be raised on error.

    This function will *NOT* attempt to verify that the devices exist in
    the Tango database, nor that they are running.

    The definitions would typically be provided by the Tango device property
    "GroupDefinitions", available in the SKABaseDevice.  The property is
    an array of strings.  Thus a sequence is expected for this function.

    Each string in the list is a JSON serialised dict defining the "group_name",
    "devices" and "subgroups" in the group.  The tango.Group() created enables
    easy access to the managed devices in bulk, or individually. Empty and
    whitespace-only strings will be ignored.

    The general format of the list is as follows, with optional "devices" and
    "subgroups" keys:
        [ {"group_name": "<name>",
           "devices": ["<dev name>", ...]},
          {"group_name": "<name>",
           "devices": ["<dev name>", "<dev name>", ...],
           "subgroups" : [{<nested group>},
                          {<nested group>}, ...]},
          ...
          ]

    For example, a hierarchy of racks, servers and switches:
    [ {"group_name": "servers",
       "devices": ["elt/server/1", "elt/server/2",
                   "elt/server/3", "elt/server/4"]},
      {"group_name": "switches",
       "devices": ["elt/switch/A", "elt/switch/B"]},
      {"group_name": "pdus",
       "devices": ["elt/pdu/rackA", "elt/pdu/rackB"]},
      {"group_name": "racks",
       "subgroups": [
            {"group_name": "rackA",
             "devices": ["elt/server/1", "elt/server/2",
                         "elt/switch/A", "elt/pdu/rackA"]},
            {"group_name": "rackB",
             "devices": ["elt/server/3", "elt/server/4",
                         "elt/switch/B", "elt/pdu/rackB"],
             "subgroups": []}
       ]} ]


    Parameters
    ----------
    json_definitions: sequence of str
        Sequence of strings, each one a JSON dict with keys "group_name", and
        one or both of:  "devices" and "subgroups", recursively defining
        the hierarchy.

    Returns
    -------
    groups: dict
        The keys of the dict are the names of the groups, in the following form:
            {"<group name 1>": <tango.Group>,
             "<group name 2>": <tango.Group>, ...}.
        Will be an empty dict if no groups were specified.

    Raises
    ------
    GroupDefinitionsError:
        - If error parsing JSON string.
        - If missing keys in the JSON definition.
        - If invalid device name.
        - If invalid groups included.
        - If a group has multiple parent groups.
        - If a device is included multiple time in a hierarchy.
          E.g. g1:[a,b] g2:[a,c] g3:[g1,g2]

    """
    try:
        # Parse and validate user's definitions
        groups = {}
        for json_definition in json_definitions:
            json_definition = json_definition.strip()
            if json_definition:
                definition = json_loads_byteified(json_definition)
                _validate_group(definition)
                group_name = definition['group_name']
                groups[group_name] = _build_group(definition)
        return groups

    except Exception as exc:
        # the exc_info is included for detailed traceback
        ska_error = SKABaseError(exc)
        raise GroupDefinitionsError(ska_error).with_traceback(sys.exc_info()[2])
        #raise GroupDefinitionsError(exc), None, sys.exc_info()[2]


def _validate_group(definition):
    """Validate and clean up groups definition, raise AssertError if invalid.

    Used internally by `get_groups_from_json`.

    """
    error_message = "Missing 'group_name' key - {}".format(definition)
    assert 'group_name' in definition, error_message
    error_message = "Missing 'devices' or 'subgroups' key - {}".format(definition)
    assert 'devices' in definition or 'subgroups' in definition, error_message

    definition['group_name'] = definition['group_name'].strip()

    old_devices = definition.get('devices', [])
    new_devices = []
    for old_device in old_devices:
        # sanity check on device name, expect 'domain/family/member'
        # TODO (AJ): Check with regex.  Allow fully qualified names?
        device = old_device.strip()
        error_message = "Invalid device name format - {}".format(device)
        assert device.count('/') == 2, error_message
        new_devices.append(device)
    definition['devices'] = new_devices

    subgroups = definition.get('subgroups', [])
    for subgroup_definition in subgroups:
        _validate_group(subgroup_definition)  # recurse


def _build_group(definition):
    """Returns tango.Group object according to defined hierarchy.

    Used internally by `get_groups_from_json`.

    """
    group_name = definition['group_name']
    devices = definition.get('devices', [])
    subgroups = definition.get('subgroups', [])

    group = tango.Group(group_name)
    for device_name in devices:
        group.add(device_name)
    for subgroup_definition in subgroups:
        subgroup = _build_group(subgroup_definition)  # recurse
        group.add(subgroup)

    return group


def validate_capability_types(
        command_name, requested_capabilities, valid_capabilities):
    """Check the validity of the input parameter passed on to the command specified
    by the command_name parameter.

    Parameters
    ----------
    command_name: str
        The name of the command which is to be executed.
    requested_capabilities: list
        A list of strings representing capability types.
    valid_capabilities: list
        A list of strings representing capability types.
    Raises
    ------
    tango.DevFailed: If any of the capabilities requested are not valid.
    """
    invalid_capabilities = list(
        set(requested_capabilities) - set(valid_capabilities))

    if invalid_capabilities:
        Except.throw_exception(
            "Command failed!", "Invalid capability types requested {}".format(
                invalid_capabilities), command_name, ErrSeverity.ERR)


def validate_input_sizes(command_name, argin):
    """Check the validity of the input parameters passed on to the command specified
    by the command_name parameter.

    Parameters
    ----------
    command_name: str
        The name of the command which is to be executed.
    argin: tango.DevVarLongStringArray
        A tuple of two lists.

    Raises
    ------
    tango.DevFailed: If the two lists are not equal in length.
    """
    capabilities_instances, capability_types = argin
    if len(capabilities_instances) != len(capability_types):
        Except.throw_exception("Command failed!", "Argin value lists size mismatch.",
                               command_name, ErrSeverity.ERR)


def convert_dict_to_list(dictionary):
    the_list = []
    for key, value in (list(dictionary.items())):
        the_list.append("{}:{}".format(key, value))

    return sorted(the_list)
