#!/usr/bin/env python

import json

import fandango as fn

def main():
    astor = fn.Astor()

    with open("/home/refelt_config_starter.json") as config_file:
        facility_data = json.load(config_file)

    server_data = facility_data['servers']
    
    for server in server_data:
        server_host = server["server_host"]
        server_name = server["server_name"]
        server_instances = server["server_instances"]

        for server_instance in server_instances:
            server_instance_name = server_instance["instance_name"]
            server_instance_starter_level = server_instance["startup_level"]
    
            srv_name = server_name + '/' + server_instance_name
            print "Starting server: ", srv_name 
            astor.set_server_level(server_name, server_host,
                server_instance_starter_level)

    astor.start_all_servers()           

if __name__ == "__main__":
    print "Starting up the servers in the facility."
    main()
