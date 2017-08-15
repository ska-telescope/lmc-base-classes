import ast
import pydoc
import inspect
import sys
import traceback

from datetime import datetime
from time import sleep

import PyTango
from PyTango import DeviceProxy, DbDatum, DevState, DbDevInfo, AttrQuality, AttrWriteType
from PyTango import Database, DbDevInfo, DeviceProxy
from PyTango._PyTango import DevState as _DevState
from contextlib import contextmanager


int_types = {PyTango._PyTango.CmdArgType.DevUShort, PyTango._PyTango.CmdArgType.DevLong,
             PyTango._PyTango.CmdArgType.DevInt,
             PyTango._PyTango.CmdArgType.DevULong,
             PyTango._PyTango.CmdArgType.DevULong64, PyTango._PyTango.CmdArgType.DevLong64,
             PyTango._PyTango.CmdArgType.DevShort}

float_types = {PyTango._PyTango.CmdArgType.DevDouble, PyTango._PyTango.CmdArgType.DevFloat}

# TBD - investigate just using (command argin data_type)
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
                         PyTango.CmdArgType.DevState.real: 'state',
                         PyTango.CmdArgType.DevVoid.real: 'void',
                         PyTango.CmdArgType.DevEnum.real: 'enum',
                         }
# TBD - not all PyTango types are used
#PyTango.CmdArgType.ConstDevString           PyTango.CmdArgType.DevState                 PyTango.CmdArgType.DevVarLong64Array        PyTango.CmdArgType.conjugate
#PyTango.CmdArgType.DevBoolean               PyTango.CmdArgType.DevString                PyTango.CmdArgType.DevVarLongArray          PyTango.CmdArgType.denominator
#PyTango.CmdArgType.DevDouble                PyTango.CmdArgType.DevUChar                 PyTango.CmdArgType.DevVarLongStringArray    PyTango.CmdArgType.imag
#PyTango.CmdArgType.DevEncoded               PyTango.CmdArgType.DevULong                 PyTango.CmdArgType.DevVarShortArray         PyTango.CmdArgType.mro
#PyTango.CmdArgType.DevEnum                  PyTango.CmdArgType.DevULong64               PyTango.CmdArgType.DevVarStateArray         PyTango.CmdArgType.name
#PyTango.CmdArgType.DevFloat                 PyTango.CmdArgType.DevUShort                PyTango.CmdArgType.DevVarStringArray        PyTango.CmdArgType.names
#PyTango.CmdArgType.DevInt                   PyTango.CmdArgType.DevVarBooleanArray       PyTango.CmdArgType.DevVarULong64Array       PyTango.CmdArgType.numerator
#PyTango.CmdArgType.DevLong                  PyTango.CmdArgType.DevVarCharArray          PyTango.CmdArgType.DevVarULongArray         PyTango.CmdArgType.real
#PyTango.CmdArgType.DevLong64                PyTango.CmdArgType.DevVarDoubleArray        PyTango.CmdArgType.DevVarUShortArray        PyTango.CmdArgType.values
#PyTango.CmdArgType.DevPipeBlob              PyTango.CmdArgType.DevVarDoubleStringArray  PyTango.CmdArgType.DevVoid
#PyTango.CmdArgType.DevShort                 PyTango.CmdArgType.DevVarFloatArray

@contextmanager
def exception_manager(cls, arguments="", callback=None):
    try:
        yield

    except PyTango.DevFailed as df:
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

        ###cls.exception(command_name=class_name + "::" + calframe[2][3],
        ###                          command_inputs=str(arguments),
        ###                          message=message)

        if callback:
            callback()

        PyTango.Except.re_throw_exception(df,
                                          "SKA_CommandFailed",
                                          message,
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

        ###cls.exception(command_name=class_name+"::"+calframe[2][3],
        ###                          command_inputs=str(arguments),
        ###                          message=message)

        if callback:
            callback()

        PyTango.Except.throw_exception("SKA_CommandFailed",
                                       message,
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

    # TBD - use tango_type_conversion dict, or just str(attribute.data_format)
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
        except Exception as ex:
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
