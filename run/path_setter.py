import sys
import os
# # import from package lmc_api
# sys.path.append('..')
# # pogo inheritance imports the class by name so we need to make the inheritance classes available in path
# sys.path.append('../lmc_api/servers/abstract')

print sys.argv
cwd = os.path.dirname(sys.argv[0])
if len(cwd):
    os.chdir(cwd)

sys.path.append("..")
server_paths = ["../skabase/src/eltlogger",
                "../skabase/src/eltmaster"]

sys.path.extend(["../skabase/src/core"])
sys.path.extend(server_paths)
