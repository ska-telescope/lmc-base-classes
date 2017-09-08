#!/usr/bin/env python

import json

import fandango as fn

def main():
    astor = fn.Astor()

    with open("/home/refelt_config_starter.json") as config_file:
        facility_data = json.load(config_file)

    hosts_data = facility_data["tango_hosts"]

    for host_name, host_data in hosts_data.items():

        for data in host_data:
            srv_instance_startup_level = data["startup_level"]
            server_instances = data["server_instances"]

            for server_instance in server_instances:
                astor.set_server_level(server_instance, host_name,
                                       srv_instance_startup_level)

            print "Starting up the servers on host=", host_name
            astor.start_servers(servers_list=server_instances, host=host_name)

if __name__ == "__main__":
    main()
