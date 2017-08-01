#!/usr/bin/env python

import os
import sys
import platform
import argparse

import PyTango
import psutil
import json
import logging
from logging import config

from time import sleep
from PyTango import Database, DbDevInfo, DeviceProxy

sys.path.append('..')
from eltbase.config import config, CONFIG_FILE

LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s [%(process)s] [%(levelname)s] [%(module)s] %(message)s',
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
        'simple': {
            'format': '%(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'aavs.ctl': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'aavs.none': {
            'handlers': [],
            'level': 'DEBUG',
        }
    }
}
logging.config.dictConfig(LOGGING)

db = Database()


def setup_tango_config(loaded_config):
    """ Set up tango configuration """
    devices = loaded_config["devices"]
    domain = loaded_config["domain"]
    default_logging_target = loaded_config["default_logging_target"]
    default_logging_level = loaded_config["default_logging_level"]

    for group_name, instances in devices.iteritems():
        for device_id, config in instances.iteritems():

            device_class = config["class"]
            full_device_name = "/".join([domain, group_name, device_id])
            device_server_name = config.get("server", None)
            device_server_id = config.get("server_id", domain)

            db.put_device_property(full_device_name, {"logging_level": default_logging_level,
                                                      "logging_target": default_logging_target})

            # Set up all properties, substituting the actual value of domain for {domain}
            for property_name, property_value in config["properties"].iteritems():
                if type(property_value) is list:
                    formatted_val = map(lambda x: x.format(domain=domain), property_value)
                else:
                    try:
                        formatted_val = property_value.format(domain=domain)
                    except Exception as e:
                        formatted_val = property_value
                db.put_device_property(full_device_name, {str(property_name): formatted_val})

            if group_name == "rack" and config.get("components"):
                db.put_device_property(full_device_name, {"rack_components": json.dumps(config["components"])})

            if device_server_name is None:
                print "No device server specified for %s" % device_class
                exit()

            dev_info = DbDevInfo()
            dev_info._class = device_class
            dev_info.server = '%s/%s' % (device_server_name, device_server_id)
            dev_info.name = full_device_name
            db.add_device(dev_info)


def _get_servers(loaded_config):
    """ Get list of servers from configuration """
    devices = loaded_config["devices"]
    priorities = loaded_config["server_priorities"]
    default_priority = max(priorities.itervalues()) + 1

    servers = set()
    server_names = set()

    for group_name, instances in devices.iteritems():
        for device_id, config in instances.iteritems():
            device_server_name = config.get("server", None)
            is_python_server = config.get("python_server", True)
            priority = priorities.get(device_server_name, default_priority)

            if device_server_name not in server_names:
                servers.add((device_server_name, is_python_server, priority))
                server_names.add(device_server_name)

    sorted_servers = sorted(servers, key=lambda x: x[2])
    return sorted_servers


def status(use_json=False):
    """ Check server configuration """
    hostname = platform.uname()[1]
    starter = "tango/admin/" + hostname
    starter_dp = DeviceProxy(starter)
    log_file_location = starter_dp.get_property("LogFileHome")["LogFileHome"][0]

    running_servers = set(starter_dp.DevGetRunningServers(True))
    domain = config["domain"]
    if servers.issubset(running_servers):
        info = json.dumps({
            "config_file": CONFIG_FILE,
            "log_location": log_file_location,
            "status": "OK",
            "servers_configured": list(servers),
            "servers_running": list(running_servers),
        }, indent=4)
        if use_json:
            print info
        else:
            log.info(info)
    else:
        not_running = servers.difference(running_servers)

        if use_json:
            print json.dumps({
                "config_file": CONFIG_FILE,
                "log_location": log_file_location,
                "servers_configured": list(servers),
                "servers_running": list(running_servers),
                "servers_not_running": list(not_running),
                "status": "FAULT"
            }, indent=4)
        else:
            for s in not_running:
                log.info("Configured server {} is not running".format(s))


def kill_everything(starter_dp, servers):
    """ Kill all running servers and remove from database """

    # Get list of running servers and stop them
    running_servers = starter_dp.DevGetRunningServers(True)
    for server in running_servers:
        starter_dp.DevStop(server)

    # Wait for servers to stop
    while starter_dp.DevGetRunningServers(True):
        log.info("Waiting for servers to stop")
        sleep(2)

    # Get list of processes which are still running
    existing_processes = [p for p in psutil.process_iter()
                          if len(p.cmdline()) > 1
                          and p.name() in {s[0] for s in servers}]

    # Kill these processes
    for p in existing_processes:
        log.info("Process {} pid {} is not dead. Killing".format(" ".join(p.cmdline()), p.pid))
        try:
            p.kill()
        except psutil.AccessDenied as ad:
            log.info("Could not kill process {}. Try running as root".format(p.pid))

    # Get list of device servers registered in database (and remove list of default tango servers)
    servers = set(db.get_server_list().value_string) - {'DataBaseds/2', 'TangoAccessControl/1', 'TangoTest/test',
                                                        'Starter/%s' % platform.uname()[1]}
    # Remove servers from database
    for server in servers:
        try:
            db.delete_server(server)
        except Exception as e:
            print e.message

# Script entry point
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Bootstrap')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--run', action="store_true", default=False, help="Stop all devices, reconfigure and run")
    group.add_argument('--status', action="store_true", default=False, help="Print the status of the tango servers")
    group.add_argument('--config', action="store_true", default=False, help="Stop all devices and reconfigure")
    group.add_argument('--stop', action="store_true", default=False, help="Print the status of the tango servers")
    parser.add_argument('--use_json', action="store_true", default=False, help="Return output as json")

    args = parser.parse_args()
    domain = config["domain"]
    servers = _get_servers(config)

    log = logging.getLogger('aavs.ctl')
    if args.use_json:
        log.disabled = True

    # TODO move prints to logging, output to json for all branches
    hostname = platform.uname()[1]
    starter = "tango/admin/" + hostname
    starter_dp = DeviceProxy(starter)

    if args.status:
        status(args.use_json)
        exit()
    elif args.stop:
        kill_everything(starter_dp, servers)
        exit()
    elif args.config or args.run:
        kill_everything(starter_dp, servers)
        # Setup all configuration
        setup_tango_config(config)

        if args.use_json:
            exit()
        else:
            log.info("Configured with {}".format(CONFIG_FILE))

    if args.run:
        db = PyTango.Database()

        # Start all required device servers
        for server, _, priority in servers:
            server_name = server + "/" + domain
            server_info = db.get_server_info(server_name)
            server_info.level = priority
            server_info.mode = 1
            server_info.host = hostname
            db.put_server_info(server_info)
            try:
                # Start device server
                starter_dp.DevStart(server_name)

                # Wait for server to finish loading
                class_name = db.get_device_class_list(server_name).value_string[3]
                sleep(0.5)
                retries = 0
                while len(db.get_device_exported_for_class(class_name).value_string) == 0 and retries < 20:
                    log.info("Waiting for {} to start".format(server_name))
                    retries += 1
                    sleep(1)

                if retries == 20:
		    raise Exception("Could not load {}".format(server_name))

            except Exception as e:
                print e
            else:
                log.info("Started {}".format(server_name))
