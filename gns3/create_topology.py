"""Create iot simulation topology."""

import sys
import time

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
    project = create_project(server, PROJECT_NAME, 2000, 4000)
    print("Created project ", project)

open_project_if_closed(server, project)

if len(get_all_nodes(server, project)) > 0:
    print("Project is not empty!")
    sys.exit(1)

# Create the templates manually using the GNS3 GUI
# get templates
templates = get_all_templates(server)

# get template ids
router_template_id = template_id_from_name(templates, "VyOS 1.3.0")
assert router_template_id
switch_template_id = template_id_from_name(templates, "Open vSwitch")
assert switch_template_id

############
# TOPOLOGY #
############

coord_rnorth = Position(0, -300)
coord_rwest = Position(-150, -75)
coord_reast = Position(150, -75)

# backbone routers
rnorth = create_node(server, project, coord_rnorth.x, coord_rnorth.y, router_template_id)
rwest = create_node(server, project, coord_rwest.x, coord_rwest.y, router_template_id)
reast = create_node(server, project, coord_reast.x, coord_reast.y, router_template_id)

create_link(server, project, rnorth["node_id"], 1, rwest["node_id"], 1)
create_link(server, project, rnorth["node_id"], 2, reast["node_id"], 1)
create_link(server, project, rwest["node_id"], 2, reast["node_id"], 2)

# router installation and configuration. TODO in parallel?
backbone_routers = [rnorth, rwest, reast]
backbone_configs = ["../router/backbone/router_north.sh",
                    "../router/backbone/router_west.sh",
                    "../router/backbone/router_east.sh"]
for router_node, config in zip(backbone_routers, backbone_configs):
    print(f"Installing {router_node['name']}")
    hostname, port = get_node_telnet_host_port(server, project, router_node["node_id"])
    terminal_cmd = f"konsole -e telnet {hostname} {port}"
    start_node(server, project, router_node["node_id"])
    install_vyos_image_on_node(router_node["node_id"], hostname, port, pre_exec=terminal_cmd)
    # time to close the terminals, else Telnet throws EOF errors
    time.sleep(10)
    print(f"Configuring {router_node['name']} with {config}")
    start_node(server, project, router_node["node_id"])
    configure_vyos_image_on_node(router_node["node_id"], hostname, port, config, pre_exec=terminal_cmd)
    time.sleep(10)

# backbone switches
coord_snorth = Position(coord_rnorth.x, coord_rnorth.y - 150)
coord_swest = Position(coord_rwest.x - 300, coord_rwest.y)
coord_seast = Position(coord_reast.x + 300, coord_reast.y)

snorth = create_node(server, project, coord_snorth.x, coord_snorth.y, switch_template_id)
swest = create_node(server, project, coord_swest.x, coord_swest.y, switch_template_id)
seast = create_node(server, project, coord_seast.x, coord_seast.y, switch_template_id)

create_link(server, project, rnorth["node_id"], 0, snorth["node_id"], 0)
create_link(server, project, rwest["node_id"], 0, swest["node_id"], 0)
create_link(server, project, reast["node_id"], 0, seast["node_id"], 0)

# west zone routers and switches
routers_west_zone = []
coords_west_zone = []
switch_freeport = 1
for i in [-3, -1, 1, 3]:
    coord = Position(coord_swest.x + 150*i, coord_swest.y + 150)
    rzone = create_node(server, project, coord.x, coord.y, router_template_id)
    create_link(server, project, rzone["node_id"], 1, swest["node_id"], switch_freeport)
    switch_freeport += 1
    coord = Position(coord.x, coord.y + 150)
    szone = create_node(server, project, coord.x, coord.y, switch_template_id)
    create_link(server, project, rzone["node_id"], 0, szone["node_id"], 0)
    routers_west_zone.append(rzone)
    coords_west_zone.append(coord)

# router installation and configuration
rwest_configs = [f"../router/locations/router_loc{i}" for i in range(1, 5)]

for router_node, config in zip(routers_west_zone, rwest_configs):
    print(f"Installing {router_node['name']}")
    hostname, port = get_node_telnet_host_port(server, project, router_node["node_id"])
    terminal_cmd = f"konsole -e telnet {hostname} {port}"
    start_node(server, project, router_node["node_id"])
    install_vyos_image_on_node(router_node["node_id"], hostname, port, pre_exec=terminal_cmd)
    # time to close the terminals, else Telnet throws EOF errors
    time.sleep(10)
    print(f"Configuring {router_node['name']} with {config}")
    start_node(server, project, router_node["node_id"])
    configure_vyos_image_on_node(router_node["node_id"], hostname, port, config, pre_exec=terminal_cmd)
    time.sleep(10)

# east zone routers and switches
routers_east_zone = []
coords_east_zone = []
switch_freeport = 1
for i in [-2, 0, 2]:
    coord = Position(coord_seast.x + 150*i, coord_seast.y + 150)
    rzone = create_node(server, project, coord.x, coord.y, router_template_id)
    create_link(server, project, rzone["node_id"], 1, seast["node_id"], switch_freeport)
    switch_freeport += 1
    coord = Position(coord.x, coord.y + 150)
    szone = create_node(server, project, coord.x, coord.y, switch_template_id)
    create_link(server, project, rzone["node_id"], 0, szone["node_id"], 0)
    routers_east_zone.append(rzone)
    coords_east_zone.append(coord)

# router installation and configuration
reast_configs = [f"../router/locations/router_loc{i}" for i in range(5, 8)]

for router_node, config in zip(routers_west_zone, reast_configs):
    print(f"Installing {router_node['name']}")
    hostname, port = get_node_telnet_host_port(server, project, router_node["node_id"])
    terminal_cmd = f"konsole -e telnet {hostname} {port}"
    start_node(server, project, router_node["node_id"])
    install_vyos_image_on_node(router_node["node_id"], hostname, port, pre_exec=terminal_cmd)
    # time to close the terminals, else Telnet throws EOF errors
    time.sleep(10)
    print(f"Configuring {router_node['name']} with {config}")
    start_node(server, project, router_node["node_id"])
    configure_vyos_image_on_node(router_node["node_id"], hostname, port, config, pre_exec=terminal_cmd)
    time.sleep(10)
