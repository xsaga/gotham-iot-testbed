"""Create iot simulation topology."""

import ipaddress
import json
import time

import requests

from gns3utils import *

PROJECT_NAME = "iot_sim"

check_resources()
check_local_gns3_config()
server = Server(*read_local_gns3_config())

req_version = requests.get(f"http://{server.addr}:{server.port}/v2/version", auth=(server.user, server.password))
req_version.raise_for_status()
print(req_version.json())

req_projects = requests.get(f"http://{server.addr}:{server.port}/v2/projects", auth=(server.user, server.password))
req_projects.raise_for_status()
projects: List[Dict[str, Any]] = req_projects.json()
print(len(projects), " projects")
if projects:
    for p in projects:
        print(f"Name='{p['name']}', ID='{p['project_id']}'")

filtered_projects = list(filter(lambda x: x["name"]==PROJECT_NAME, projects))
if filtered_projects:
    p = filtered_projects[0]
    project = Project(name=p["name"], id=p["project_id"], grid_unit=int(p["grid_size"]*1.4))
    print(f"Project {PROJECT_NAME} exists. ", project)
else:
    # create the project
    # http://api.gns3.net/en/2.2/api/v2/controller/project/projects.html
    # Coordinate 0,0 is located in the center of the project
    payload_project = {"name": PROJECT_NAME, "show_grid": True, "scene_height": 2000, "scene_width": 4000}
    r = requests.post(f"http://{server.addr}:{server.port}/v2/projects", data=json.dumps(payload_project), auth=(server.user, server.password))
    r.raise_for_status()
    p = r.json()
    project = Project(name=p["name"], id=p["project_id"], grid_unit=int(p["grid_size"]*1.4))
    assert project.name == PROJECT_NAME
    print("Created project ", project)

# open project if closed
if p["status"] == "closed":
    r = requests.post(f"http://{server.addr}:{server.port}/v2/projects/{project.id}/open", data={}, auth=(server.user, server.password))
    r.raise_for_status()
    assert r.json()["status"] == "opened"

# Por ahora crear los templates en GNS3 GUI
# get templates
r = requests.get(f"http://{server.addr}:{server.port}/v2/templates", auth=(server.user, server.password))
r.raise_for_status()
templates = r.json()

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

# routers
rnorth = create_node(server, project, coord_rnorth.x, coord_rnorth.y, router_template_id)
rwest = create_node(server, project, coord_rwest.x, coord_rwest.y, router_template_id)
reast = create_node(server, project, coord_reast.x, coord_reast.y, router_template_id)

create_link(server, project, rnorth["node_id"], 1, rwest["node_id"], 1)
create_link(server, project, rnorth["node_id"], 2, reast["node_id"], 1)
create_link(server, project, rwest["node_id"], 2, reast["node_id"], 2)

# installation and configuration
# TODO in parallel?
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

# switches
coord_snorth = Position(coord_rnorth.x, coord_rnorth.y - 150)
coord_swest = Position(coord_rwest.x - 300, coord_rwest.y)
coord_seast = Position(coord_reast.x + 300, coord_reast.y)

snorth = create_node(server, project, coord_snorth.x, coord_snorth.y, switch_template_id)
swest = create_node(server, project, coord_swest.x, coord_swest.y, switch_template_id)
seast = create_node(server, project, coord_seast.x, coord_seast.y, switch_template_id)

create_link(server, project, rnorth["node_id"], 0, snorth["node_id"], 0)
create_link(server, project, rwest["node_id"], 0, swest["node_id"], 0)
create_link(server, project, reast["node_id"], 0, seast["node_id"], 0)

# routers west zone
routers_west_zone = []
coords_west_zone = []
swest_freeport = 1
for i in [-3, -1, 1, 3]:
    coord_rwz = Position(coord_swest.x + 150*i, coord_swest.y + 150)
    rwz = create_node(server, project, coord_rwz.x, coord_rwz.y, router_template_id)
    create_link(server, project, rwz["node_id"], 1, swest["node_id"], swest_freeport)
    swest_freeport += 1
    swz = create_node(server, project, coord_rwz.x, coord_rwz.y + 150, switch_template_id)
    create_link(server, project, rwz["node_id"], 0, swz["node_id"], 0)
    routers_west_zone.append(rwz)
    coords_west_zone.append(coord_rwz)

# routers east zone
routers_east_zone = []
coords_east_zone = []
seast_freeport = 1
for i in [-2, 0, 2]:
    coord_rez = Position(coord_seast.x + 150*i, coord_seast.y + 150)
    rez = create_node(server, project, coord_rez.x, coord_rez.y, router_template_id)
    create_link(server, project, rez["node_id"], 1, seast["node_id"], seast_freeport)
    seast_freeport += 1
    sez = create_node(server, project, coord_rez.x, coord_rez.y + 150, switch_template_id)
    create_link(server, project, rez["node_id"], 0, sez["node_id"], 0)
    routers_east_zone.append(rez)
    coords_east_zone.append(coord_rez)
