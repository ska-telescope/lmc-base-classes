import ast
import pydoc
from datetime import datetime
from time import sleep

import PyTango
from PyTango import DeviceProxy, DbDatum, DevState, DbDevInfo, AttrQuality, AttrWriteType
from PyTango._PyTango import DevState as _DevState

int_types = {PyTango._PyTango.CmdArgType.DevUShort, PyTango._PyTango.CmdArgType.DevLong,
             PyTango._PyTango.CmdArgType.DevInt,
             PyTango._PyTango.CmdArgType.DevULong,
             PyTango._PyTango.CmdArgType.DevULong64, PyTango._PyTango.CmdArgType.DevLong64,
             PyTango._PyTango.CmdArgType.DevShort}

float_types = {PyTango._PyTango.CmdArgType.DevDouble, PyTango._PyTango.CmdArgType.DevFloat}

tango_type_conversion = {PyTango.CmdArgType.DevUShort.real: 'int',
                            PyTango.CmdArgType.DevLong.real: 'int',
                            PyTango.CmdArgType.DevInt.real: 'int',
                            PyTango.CmdArgType.DevULong.real: 'int',
                            PyTango.CmdArgType.DevULong64.real: 'int',
                            PyTango.CmdArgType.DevLong64.real: 'int',
                            PyTango.CmdArgType.DevShort.real: 'int',
                            PyTango.CmdArgType.DevDouble.real: 'float',
                            PyTango.CmdArgType.DevFloat.real: 'float',
                            PyTango.CmdArgType.DevString.real: 'str',
                            PyTango.CmdArgType.DevBoolean.real: 'bool',
                            PyTango.CmdArgType.DevEncoded.real: 'encoded',
                            PyTango.CmdArgType.DevState.real: '',
                            PyTango.CmdArgType.DevVoid.real: 'void'}


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


def wait_seconds(dp, max=3):
    i = 0
    while (dp.state() != DevState.ALARM) and i < max:
        sleep(1)
        i += 1


VALID_TYPES = ['int', 'bool', 'str', 'float']


def convert_api_value(param_dict):
    """
    Used to validate tango command parameters which are passed via json
    :param param_dict:
    :return:
    """
    type_str = param_dict.get('type', 'str').lower()
    if type_str not in VALID_TYPES:
        raise Exception('Valid types must be from %s' % ', '.join(VALID_TYPES))

    value_type = pydoc.locate(type_str)
    if value_type == bool:
        if not param_dict.get('value').lower() in ['true', 'false']:
            raise Exception('Parameter value %s is not of type %s' % (param_dict.get('value'), value_type))
        value = param_dict.get('value').lower() == 'true'
    else:
        value = value_type(param_dict.get('value'))
    return param_dict.get('name'), value


def coerce_value(value):
    # Enum is not serialised correctly as json
    # _DevState  is PyTango._PyTango.DevState
    # because DevState  is PyTango._PyTango.DevState != PyTango.DevState
    if type(value) in [DevState, _DevState]:
        return str(value)
    return value


def get_dp_attribute(device_proxy, attribute, with_value=False, with_context=False):
    attr_dict = {
        'name': attribute.name,
        'polling_frequency': attribute.events.per_event.period,
        'min_value': attribute.min_value if attribute.min_value != 'Not specified' else None,
        'max_value': attribute.max_value if attribute.min_value != 'Not specified' else None,
        'readonly': attribute.writable not in [AttrWriteType.READ_WRITE, AttrWriteType.WRITE,
                                               AttrWriteType.READ_WITH_WRITE]
    }

    if attribute.data_format == PyTango._PyTango.AttrDataFormat.SCALAR:
        if attribute.data_type in int_types:
            attr_dict["data_type"] = "int"
        elif attribute.data_type in float_types:
            attr_dict["data_type"] = "float"
        elif attribute.data_type == PyTango._PyTango.CmdArgType.DevString:
            attr_dict["data_type"] = "str"
        elif attribute.data_type == PyTango._PyTango.CmdArgType.DevBoolean:
            attr_dict["data_type"] = "bool"
        elif attribute.data_type == PyTango._PyTango.CmdArgType.DevEncoded:
            attr_dict["data_type"] = "encoded"
        elif attribute.data_type == PyTango._PyTango.CmdArgType.DevVoid:
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
        except Exception, ex:
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
