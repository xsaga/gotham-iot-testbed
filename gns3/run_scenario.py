"""Run scenario using the iot simulation topology."""

import sys

from gns3utils import *

PROJECT_NAME = "iot_sim"

check_resources()
check_local_gns3_config()
server = Server(*read_local_gns3_config())

check_server_version(server)

project = get_project_by_name(server, PROJECT_NAME)

if project:
    print(f"Project {PROJECT_NAME} exists. ", project)
else:
    print(f"Project {PROJECT_NAME} does not exsist!")
    sys.exit(1)

open_project_if_closed(server, project)

if len(get_all_nodes(server, project)) == 0:
    print(f"Project {PROJECT_NAME} is empty!")
    sys.exit(1)

#######
# Run #
#######

start_all_routers(server, project)
start_all_switches(server, project)
start_all_iot(server, project)
