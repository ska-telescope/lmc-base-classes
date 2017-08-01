from PyTango import Database, DbDevInfo
import os, signal

# A reference on the Database
db = Database()

# Kill running servers
# Get device info of Tile
try:
    dev_info = db.get_device_info('test/tile/1')
    if dev_info.pid != 0:
       os.kill(dev_info.pid, signal.SIGTERM)  #o r signal.SIGKILL
    print "Killed PID: %s" % dev_info.pid
except Exception as ex:
    print "No process to kill for test/tile/1"

#get device info of ObsConf
try:
    dev_info = db.get_device_info('test/obsconf/1')
    if dev_info.pid != 0:
       os.kill(dev_info.pid, signal.SIGTERM)  #o r signal.SIGKILL
    print "Killed PID: %s" % dev_info.pid
except Exception as ex:
    print "No process to kill for test/obsconf/1"

#get device info of TPM
try:
    dev_info = db.get_device_info('test/tpm_board/1')
    if dev_info.pid != 0:
       os.kill(dev_info.pid, signal.SIGTERM)
    print "Killed PID: %s" % dev_info.pid
except Exception as ex:
    print "No process to kill for test/tpm_board/1"



#get device info of Tile
def tile_device_info(device_id):
    device_name = 'test/tile/%s' % device_id
    try:
        dev_info = db.get_device_info(device_name)
    except Exception as ex:
        dev_info = None
    if not dev_info is None:
        print "Device <<%s>> found:" % device_name
        print "Name: %s" % (dev_info.name)
        print "Class Name: %s" % (dev_info.class_name)
        print "Full Name: %s" % (dev_info.ds_full_name)
        print "Exported: %s" % (dev_info.exported)
        print "IOR: %s" % (dev_info.ior)
        print "Version: %s" % (dev_info.version)
        print "PID: %s" % (dev_info.pid)
        print "Started Date: %s" % (dev_info.started_date)
        print "Stopped Date: %s" % (dev_info.stopped_date)
    else:
        # Define Tile device name
        new_device_name = device_name
        # Define the Tango Class served by this DServer
        dev_info = DbDevInfo()
        dev_info._class = "Tile_DS"
        dev_info.server = "Tile_DS/test"
        # add the device
        dev_info.name = new_device_name
        print("Creating device: %s" % new_device_name)
        db.add_device(dev_info)

#get device info of TPM
def tpm_device_info(device_id):
    device_name = 'test/tpm_board/%s' % device_id
    try:
        dev_info = db.get_device_info(device_name)
    except Exception as ex:
        dev_info = None
    if not dev_info is None:
        print "Device <<%s>> found:" % device_name
        print "Name: %s" % (dev_info.name)
        print "Class Name: %s" % (dev_info.class_name)
        print "Full Name: %s" % (dev_info.ds_full_name)
        print "Exported: %s" % (dev_info.exported)
        print "IOR: %s" % (dev_info.ior)
        print "Version: %s" % (dev_info.version)
        print "PID: %s" % (dev_info.pid)
        print "Started Date: %s" % (dev_info.started_date)
        print "Stopped Date: %s" % (dev_info.stopped_date)
    else:
        # Define device name
        new_device_name = device_name
        # Define the Tango Class served by this DServer
        dev_info = DbDevInfo()
        dev_info._class = "TPM_DS"
        dev_info.server = "TPM_DS/test"
        # add the device
        dev_info.name = new_device_name
        print("Creating device: %s" % new_device_name)
        db.add_device(dev_info)

#get device info of ObsConf
def obsconf_device_info(device_id):
    device_name = 'test/obsconf/%s' % device_id
    try:
        dev_info = db.get_device_info(device_name)
    except Exception as ex:
        dev_info = None
    if not dev_info is None:
        print "Device <<%s>> found:" % device_name
        print "Name: %s" % (dev_info.name)
        print "Class Name: %s" % (dev_info.class_name)
        print "Full Name: %s" % (dev_info.ds_full_name)
        print "Exported: %s" % (dev_info.exported)
        print "IOR: %s" % (dev_info.ior)
        print "Version: %s" % (dev_info.version)
        print "PID: %s" % (dev_info.pid)
        print "Started Date: %s" % (dev_info.started_date)
        print "Stopped Date: %s" % (dev_info.stopped_date)
    else:
        # Define device name
        new_device_name = device_name
        # Define the Tango Class served by this DServer
        dev_info = DbDevInfo()
        dev_info._class = "ObservationConfiguration"
        dev_info.server = "ObservationConfiguration/test"
        # add the device
        dev_info.name = new_device_name
        print("Creating device: %s" % new_device_name)
        db.add_device(dev_info)


obsconf_device_info('main')
tpm_device_info(1)
tile_device_info(1)