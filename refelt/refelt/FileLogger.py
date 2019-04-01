import logging
import logging.handlers
import time
from PyTango.server import run, device_property
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command
import PyTango
import datetime

logger_dict = {}


class FileLogger(Device):
    __metaclass__ = DeviceMeta



    log_path = device_property(dtype=str, default_value="/tmp")

    def __init__(self, cl, name):
        super(FileLogger, self).__init__(cl, name)
        print(self.log_path)



    @command(dtype_in='DevVarStringArray', dtype_out=None)
    def log(self, details):
        # import ipdb; ipdb.set_trace()
        source_device =  details[2]
        message = details[3]
        timestamp = str(datetime.datetime.fromtimestamp(float(details[0]) / 1000))
        logger = logger_dict.get(source_device)
        if not logger:
            logger = logging.getLogger(source_device)
            logger.setLevel(logging.INFO)

            # Add the log message handler to the logger
            handler = logging.handlers.RotatingFileHandler(
                self.log_path+ "/"+source_device.replace("/", "_"), maxBytes=3000000, backupCount=5)

            logger.addHandler(handler)
            logger_dict[source_device] = logger

        logger.info("{}]\t{}".format(timestamp,message))
        # print details


def main(args=None, **kwargs):
    # PROTECTED REGION ID(FileLogger.main) ENABLED START #
    return run((FileLogger,), args=args, **kwargs)
    # PROTECTED REGION END #    //  RefA.main

if __name__ == '__main__':
    main()


#def main():
#    run((FileLogger,))

#if __name__ == "__main__":

#    db = PyTango.Database()

#    server_name = 'logger/test'
#    dev_info = PyTango.DbDevInfo()
#    dev_info._class = "FileLogger"
#    dev_info.server = server_name
#    dev_info.name =  "test/logger/1"
#    db.add_device(dev_info)

#    db.put_device_property("test/logger/1", {"log_path": "/opt/ska/log/tango"})
#    main()
