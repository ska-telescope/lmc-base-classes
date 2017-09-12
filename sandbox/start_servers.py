#!/usr/bin/env python
import json
import argparse

import fandango as fn

parser = argparse.ArgumentParser(description="A Python script used to start the TANGO"
                                             "device server processes and register them"
                                             "with Starter for automated startup")
parser.add_argument("-conf", "--config_file",
                    help="A configuration file defining the server processes to be run"
                    "by Starter.", required=True)


def main():
    args = parser.parse_args()
    astor = fn.Astor()

    with open(args.config_file) as elt_config_file:
        facility_data = json.load(elt_config_file)

    hosts_data = facility_data["tango_hosts"]

    for host_name, host_data in hosts_data.items():

        for data in host_data:
            srv_instance_startup_level = data["startup_level"]
            server_instances = data["server_instances"]

            for server_instance in server_instances:
                try:
                    astor.set_server_level(server_instance, host_name,
                                           srv_instance_startup_level)
                    # For now - start each server - else they do not show up in the
                    # Astor GUI. Start them independently since they do not all exist
                    # in DsPath yet
                    try:
                        astor.start_servers([server_instance], host=host_name)
                    except Exception as exc:
           # Do not count this as an error for now
                except Exception as exc:
                    logging.error("FAILED to register {} {}".format(
                        server_instance, exc))
                    print """FAILED TO REGISTER in ASTOR"""
                    print """host={!r}  level={!r} server_instance={!r}.""".format(
                        host_name, srv_instance_startup_level, server_instance)


if __name__ == "__main__":
    main()
