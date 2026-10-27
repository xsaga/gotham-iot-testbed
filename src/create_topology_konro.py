"""Create a reduced Gotham topology for the Konro integration (konro scenario).

Compared with create_topology_gotham.py it keeps only what the project needs,
so it is lighter to run (6 VyOS routers instead of 10, ~20 containers instead of ~100):

  CLOUD  (RNORTH, 192.168.0.0/20)    DNS, NTP, MQTT broker, Mirai bot (initial infector)
  ZONE A (RC1,    192.168.17.0/24)   3 domotic monitors (sensors)  + 2 edge workers
  ZONE B (RC2,    192.168.18.0/24)   3 hydraulic systems (sensors) + 2 edge workers
  THREAT (RT1,    192.168.33.0/24)   Mirai C&C, scan listener, loader, wget loader

Edge workers are generic compute nodes where the sensitive applications run.
Sensors and workers can be made vulnerable to Mirai at runtime (run_scenario_konro.py).

Prerequisites:
  - Gotham templates created (create_templates.py) and the VyOS 1.3.0 appliance installed.
  - Edge worker image built:
        docker build --tag iotsim/edge-worker Dockerfiles/iot/edge_worker
    (the GNS3 template "iotsim-edge-worker" is created by this script if missing).

Run from the src/ directory:  python3 create_topology_konro.py
"""

import configparser
import ipaddress
import sys
import time

from gns3utils import *

PROJECT_NAME = "konro_scenario"
AUTO_CONFIGURE_ROUTERS = True

NUM_WORKERS_PER_ZONE = 2
NUM_SENSORS_PER_ZONE = 3
SENSOR_SLEEP_TIME = 10      # seconds between telemetry messages (default in Gotham: 60)

check_resources()
check_local_gns3_config()
server = Server(*read_local_gns3_config())

check_server_version(server)

project = get_project_by_name(server, PROJECT_NAME)

if project:
    print(f"Project {PROJECT_NAME} exists. ", project)
else:
    project = create_project(server, PROJECT_NAME, 3000, 5000, 30)
    print("Created project ", project)

open_project_if_closed(server, project)

if len(get_all_nodes(server, project)) > 0:
    print("Project is not empty!")
    sys.exit(1)

#############
# TEMPLATES #
#############

templates = get_all_templates(server)


def template_id(name: str) -> str:
    tid = get_template_id_from_name(templates, name)
    assert tid, f"GNS3 template '{name}' not found"
    return tid


# create the edge worker template if it does not exist yet
if not get_template_id_from_name(templates, "iotsim-edge-worker"):
    print("Creating GNS3 template iotsim-edge-worker")
    create_docker_template(server, "iotsim-edge-worker", "iotsim/edge-worker:latest", "")
    templates = get_all_templates(server)

router_template_id = template_id("VyOS 1.3.0")
switch_template_id = template_id("Open vSwitch")
dns_template_id = template_id("iotsim-dns")
ntp_template_id = template_id("iotsim-ntp")
broker_template_id = template_id("iotsim-mqtt-broker-1.6")
domotic_template_id = template_id("iotsim-domotic-monitor")
hydraulic_template_id = template_id("iotsim-hydraulic-system")
worker_template_id = template_id("iotsim-edge-worker")
mirai_cnc_template_id = template_id("iotsim-mirai-cnc")
mirai_bot_template_id = template_id("iotsim-mirai-bot")
mirai_scan_listener_template_id = template_id("iotsim-mirai-scan-listener")
mirai_loader_template_id = template_id("iotsim-mirai-loader")
mirai_wget_loader_template_id = template_id("iotsim-mirai-wget-loader")

# read project configuration file
sim_config = configparser.ConfigParser()
with open("../iot-sim.config", "r", encoding="utf-8") as cf:
    sim_config.read_string(f"[main]\n{cf.read()}")
    sim_config = sim_config["main"]

lab_nameserver = sim_config["LAB_DNS_IPADDR"]                       # 192.168.0.2
NTP_NAME = (f"ntp.{sim_config['LOCAL_DOMAIN']}", "192.168.0.3")
BROKER_NAME = (f"broker.city.{sim_config['LOCAL_DOMAIN']}", "192.168.2.1")

input("Open the GNS3 project GUI. Press enter to continue...")


def install_and_configure_routers(routers, configs):
    """Install VyOS on each router and apply its configuration script."""
    if not AUTO_CONFIGURE_ROUTERS:
        return
    for router_node, router_config in zip(routers, configs):
        print(f"Installing {router_node['name']}")
        hostname, port = get_node_telnet_host_port(server, project, router_node["node_id"])
        terminal_cmd = f"konsole -e telnet {hostname} {port}"
        start_node(server, project, router_node["node_id"])
        install_vyos_image_on_node(router_node["node_id"], hostname, port, pre_exec=terminal_cmd)
        time.sleep(10)  # time to close the terminals, else Telnet throws EOF errors
        print(f"Configuring {router_node['name']} with {router_config}")
        start_node(server, project, router_node["node_id"])
        configure_vyos_image_on_node(router_node["node_id"], hostname, port, router_config, pre_exec=terminal_cmd)
        time.sleep(10)


def set_env(node, **values):
    """Update some environment variables of a docker node."""
    env = environment_string_to_dict(get_docker_node_environment(server, project, node["node_id"]))
    env.update({k: str(v) for k, v in values.items()})
    update_docker_node_environment(server, project, node["node_id"], environment_dict_to_string(env))


def attach_single_node(switch, switch_port, template, x, y, ip_iface, gateway, nameserver=lab_nameserver):
    """Create a node, link it to a switch port and set its static address."""
    node = create_node(server, project, x, y, template)
    create_link(server, project, switch["node_id"], switch_port, node["node_id"], 0)
    set_node_network_interfaces(server, project, node["node_id"], "eth0", ip_iface, gateway, nameserver)
    print(f"Created {node['name']} addr {ip_iface}")
    return node


############
# TOPOLOGY #
############

g = project.grid_unit

####################
# backbone routers #
####################

coord_rnorth = Position(0, -600)
coord_rwest = Position(coord_rnorth.x - g * 2, coord_rnorth.y + g * 4)
coord_reast = Position(coord_rnorth.x + g * 2, coord_rnorth.y + g * 4)

rnorth = create_node(server, project, coord_rnorth.x, coord_rnorth.y, router_template_id)
rwest = create_node(server, project, coord_rwest.x, coord_rwest.y, router_template_id)
reast = create_node(server, project, coord_reast.x, coord_reast.y, router_template_id)

create_link(server, project, rnorth["node_id"], 1, rwest["node_id"], 1)
create_link(server, project, rnorth["node_id"], 2, reast["node_id"], 1)
create_link(server, project, rwest["node_id"], 2, reast["node_id"], 2)

install_and_configure_routers([rnorth, rwest, reast],
                              ["../router/backbone/router_north.sh",
                               "../router/backbone/router_west.sh",
                               "../router/backbone/router_east.sh"])

#####################
# backbone switches #
#####################

coord_snorth = Position(coord_rnorth.x, coord_rnorth.y - g * 2)
coord_swest = Position(coord_rwest.x - g * 6, coord_rwest.y)
coord_seast = Position(coord_reast.x + g * 6, coord_reast.y)

snorth = create_node(server, project, coord_snorth.x, coord_snorth.y, switch_template_id)
swest = create_node(server, project, coord_swest.x, coord_swest.y, switch_template_id)
seast = create_node(server, project, coord_seast.x, coord_seast.y, switch_template_id)

create_link(server, project, rnorth["node_id"], 0, snorth["node_id"], 0)
create_link(server, project, rwest["node_id"], 0, swest["node_id"], 0)
create_link(server, project, reast["node_id"], 0, seast["node_id"], 0)

##############################
# edge routers and switches  #
##############################
# West: zone A (router_loc1, 192.168.17.0/24) and zone B (router_loc2, 192.168.18.0/24)
# East: threat zone (router_loc5, 192.168.33.0/24)


def create_edge_zone(backbone_switch, backbone_port, x, y):
    rzone = create_node(server, project, x, y, router_template_id)
    create_link(server, project, rzone["node_id"], 1, backbone_switch["node_id"], backbone_port)
    szone = create_node(server, project, x, y + g * 2, switch_template_id)
    create_link(server, project, rzone["node_id"], 0, szone["node_id"], 0)
    return rzone, szone, Position(x, y + g * 2)


r_zone_a, s_zone_a, coord_zone_a = create_edge_zone(swest, 1, coord_swest.x - g * 5, coord_swest.y + g * 3)
r_zone_b, s_zone_b, coord_zone_b = create_edge_zone(swest, 2, coord_swest.x + g * 5, coord_swest.y + g * 3)
r_threat, s_threat, coord_threat = create_edge_zone(seast, 1, coord_seast.x, coord_seast.y + g * 3)

install_and_configure_routers([r_zone_a, r_zone_b, r_threat],
                              ["../router/locations/router_loc1.sh",
                               "../router/locations/router_loc2.sh",
                               "../router/locations/router_loc5.sh"])

#########
# CLOUD #
#########

coord_cloud = Position(coord_snorth.x, coord_snorth.y - g * 3)
s_cloud = create_node(server, project, coord_cloud.x, coord_cloud.y, switch_template_id)
create_link(server, project, snorth["node_id"], 1, s_cloud["node_id"], 0)

dns = attach_single_node(s_cloud, 1, dns_template_id, coord_cloud.x - g * 3, coord_cloud.y - g * 2,
                         ipaddress.IPv4Interface(f"{lab_nameserver}/20"), "192.168.0.1", "127.0.0.1")
ntp = attach_single_node(s_cloud, 2, ntp_template_id, coord_cloud.x - g * 1, coord_cloud.y - g * 2,
                         ipaddress.IPv4Interface(f"{NTP_NAME[1]}/20"), "192.168.0.1")
broker = attach_single_node(s_cloud, 3, broker_template_id, coord_cloud.x + g * 1, coord_cloud.y - g * 2,
                            ipaddress.IPv4Interface(f"{BROKER_NAME[1]}/20"), "192.168.0.1")
mirai_bot = attach_single_node(s_cloud, 4, mirai_bot_template_id, coord_cloud.x + g * 3, coord_cloud.y - g * 2,
                               ipaddress.IPv4Interface("192.168.0.100/20"), "192.168.0.1")

##########
# ZONE A #
##########
# sensors: 192.168.17.10 ... ; workers: 192.168.17.50 ...

zone_a_sensors = create_cluster_of_nodes(server, project, NUM_SENSORS_PER_ZONE,
                                         coord_zone_a.x - g * 3, coord_zone_a.y + g * 2, NUM_SENSORS_PER_ZONE,
                                         switch_template_id, domotic_template_id, s_zone_a["node_id"], 1,
                                         ipaddress.IPv4Interface("192.168.17.10/24"), "192.168.17.1", lab_nameserver, 1.5)
for d in zone_a_sensors[1]:
    set_env(d, MQTT_BROKER_ADDR=BROKER_NAME[0], NTP_SERVER=NTP_NAME[0], SLEEP_TIME=SENSOR_SLEEP_TIME)

zone_a_workers = create_cluster_of_nodes(server, project, NUM_WORKERS_PER_ZONE,
                                         coord_zone_a.x + g * 3, coord_zone_a.y + g * 2, NUM_WORKERS_PER_ZONE,
                                         switch_template_id, worker_template_id, s_zone_a["node_id"], 2,
                                         ipaddress.IPv4Interface("192.168.17.50/24"), "192.168.17.1", lab_nameserver, 1.5)

##########
# ZONE B #
##########
# sensors: 192.168.18.10 ... ; workers: 192.168.18.50 ...

zone_b_sensors = create_cluster_of_nodes(server, project, NUM_SENSORS_PER_ZONE,
                                         coord_zone_b.x - g * 3, coord_zone_b.y + g * 2, NUM_SENSORS_PER_ZONE,
                                         switch_template_id, hydraulic_template_id, s_zone_b["node_id"], 1,
                                         ipaddress.IPv4Interface("192.168.18.10/24"), "192.168.18.1", lab_nameserver, 1.5)
for d in zone_b_sensors[1]:
    set_env(d, MQTT_BROKER_ADDR=BROKER_NAME[0], NTP_SERVER=NTP_NAME[0], SLEEP_TIME=SENSOR_SLEEP_TIME)

zone_b_workers = create_cluster_of_nodes(server, project, NUM_WORKERS_PER_ZONE,
                                         coord_zone_b.x + g * 3, coord_zone_b.y + g * 2, NUM_WORKERS_PER_ZONE,
                                         switch_template_id, worker_template_id, s_zone_b["node_id"], 2,
                                         ipaddress.IPv4Interface("192.168.18.50/24"), "192.168.18.1", lab_nameserver, 1.5)

#################
# THREAT (Mirai)#
#################

mirai_cnc = attach_single_node(s_threat, 1, mirai_cnc_template_id, coord_threat.x - g * 3, coord_threat.y + g * 2,
                               ipaddress.IPv4Interface(f"{sim_config['MIRAI_CNC_IPADDR']}/24"), "192.168.33.1")
mirai_scan_listener = attach_single_node(s_threat, 2, mirai_scan_listener_template_id, coord_threat.x - g * 1, coord_threat.y + g * 2,
                                         ipaddress.IPv4Interface(f"{sim_config['MIRAI_REPORT_IPADDR']}/24"), "192.168.33.1")
mirai_loader = attach_single_node(s_threat, 3, mirai_loader_template_id, coord_threat.x + g * 1, coord_threat.y + g * 2,
                                  ipaddress.IPv4Interface("192.168.33.12/24"), "192.168.33.1")
mirai_wget_loader = attach_single_node(s_threat, 4, mirai_wget_loader_template_id, coord_threat.x + g * 3, coord_threat.y + g * 2,
                                       ipaddress.IPv4Interface(f"{sim_config['MIRAI_WGET_LOADER_IPADDR']}/24"), "192.168.33.1")

#######
# DNS #
#######

EXTRA_HOSTS = {NTP_NAME[0]: NTP_NAME[1],
               BROKER_NAME[0]: BROKER_NAME[1]}
update_docker_node_extrahosts(server, project, dns["node_id"], extrahosts_dict_to_string(EXTRA_HOSTS))

check_ipaddrs(server, project)

print("\nTopology created.")
print("Sensors :", [d["name"] for d in zone_a_sensors[1] + zone_b_sensors[1]])
print("Workers :", [d["name"] for d in zone_a_workers[1] + zone_b_workers[1]])
