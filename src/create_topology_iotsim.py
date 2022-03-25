"""Create iot simulation topology (simple)."""

import configparser
import ipaddress
import sys
import time

from gns3utils import *

PROJECT_NAME = "iot_sim"
AUTO_CONFIGURE_ROUTERS = True

check_resources()
check_local_gns3_config()
server = Server(*read_local_gns3_config())

check_server_version(server)

project = get_project_by_name(server, PROJECT_NAME)

if project:
    print(f"Project {PROJECT_NAME} exists. ", project)
else:
    project = create_project(server, PROJECT_NAME, 5000, 7500, 15)
    print("Created project ", project)

open_project_if_closed(server, project)

if len(get_all_nodes(server, project)) > 0:
    print("Project is not empty!")
    sys.exit(1)

# Create the templates manually using the GNS3 GUI
# get templates
templates = get_all_templates(server)

# get template ids
router_template_id = get_template_id_from_name(templates, "VyOS 1.3.0")
assert router_template_id
switch_template_id = get_template_id_from_name(templates, "Open vSwitch")
assert switch_template_id

DNS_template_id = get_template_id_from_name(templates, "iotsim-dns")
assert DNS_template_id
certificates_template_id = get_template_id_from_name(templates, "iotsim-certificates")
assert certificates_template_id
NTP_template_id = get_template_id_from_name(templates, "iotsim-ntp")
assert NTP_template_id
Merlin_template_id = get_template_id_from_name(templates, "iotsim-merlin-cnc")
assert Merlin_template_id
Mirai_builder_template_id = get_template_id_from_name(templates, "iotsim-mirai-builder")
assert Mirai_builder_template_id
Mirai_cnc_template_id = get_template_id_from_name(templates, "iotsim-mirai-cnc")
assert Mirai_cnc_template_id
Mirai_bot_template_id = get_template_id_from_name(templates, "iotsim-mirai-bot")
assert Mirai_bot_template_id
Mirai_scan_listener_template_id = get_template_id_from_name(templates, "iotsim-mirai-scan-listener")
assert Mirai_scan_listener_template_id
Mirai_loader_template_id = get_template_id_from_name(templates, "iotsim-mirai-loader")
assert Mirai_loader_template_id
Mirai_wget_loader_template_id = get_template_id_from_name(templates, "iotsim-mirai-wget-loader")
assert Mirai_wget_loader_template_id
scanner_template_id = get_template_id_from_name(templates, "iotsim-scanner")
assert scanner_template_id
amplification_coap_template_id = get_template_id_from_name(templates, "iotsim-amplification-coap")
assert amplification_coap_template_id
mqtt_attacks_template_id = get_template_id_from_name(templates, "iotsim-mqtt-attacks")
assert mqtt_attacks_template_id
metasploit_template_id = get_template_id_from_name(templates, "iotsim-metasploit")
assert metasploit_template_id
mqtt_broker_1_6_template_id = get_template_id_from_name(templates, "iotsim-mqtt-broker-1.6")
assert mqtt_broker_1_6_template_id
mqtt_broker_1_6_auth_template_id = get_template_id_from_name(templates, "iotsim-mqtt-broker-1.6-auth")
assert mqtt_broker_1_6_auth_template_id
mqtt_broker_tls_template_id = get_template_id_from_name(templates, "iotsim-mqtt-broker-tls")
assert mqtt_broker_tls_template_id
mqtt_client_t1_template_id = get_template_id_from_name(templates, "iotsim-mqtt-client-t1")
assert mqtt_client_t1_template_id
mqtt_client_t2_template_id = get_template_id_from_name(templates, "iotsim-mqtt-client-t2")
assert mqtt_client_t2_template_id
air_quality_template_id = get_template_id_from_name(templates, "iotsim-air-quality")
assert air_quality_template_id
cooler_motor_template_id = get_template_id_from_name(templates, "iotsim-cooler-motor")
assert cooler_motor_template_id
predictive_maintenance_template_id = get_template_id_from_name(templates, "iotsim-predictive-maintenance")
assert predictive_maintenance_template_id
hydraulic_system_template_id = get_template_id_from_name(templates, "iotsim-hydraulic-system")
assert hydraulic_system_template_id
building_monitor_template_id = get_template_id_from_name(templates, "iotsim-building-monitor")
assert building_monitor_template_id
domotic_monitor_template_id = get_template_id_from_name(templates, "iotsim-domotic-monitor")
assert domotic_monitor_template_id
coap_server_template_id = get_template_id_from_name(templates, "iotsim-coap-server")
assert coap_server_template_id
coap_cloud_template_id = get_template_id_from_name(templates, "iotsim-coap-cloud")
assert coap_cloud_template_id
city_power_template_id = get_template_id_from_name(templates, "iotsim-city-power")
assert city_power_template_id
city_power_tls_template_id = get_template_id_from_name(templates, "iotsim-city-power-tls")
assert city_power_tls_template_id
combined_cycle_template_id = get_template_id_from_name(templates, "iotsim-combined-cycle")
assert combined_cycle_template_id
combined_cycle_tls_template_id = get_template_id_from_name(templates, "iotsim-combined-cycle-tls")
assert combined_cycle_tls_template_id
city_power_cloud_template_id = get_template_id_from_name(templates, "iotsim-city-power-cloud")
assert city_power_cloud_template_id
combined_cycle_cloud_template_id = get_template_id_from_name(templates, "iotsim-combined-cycle-cloud")
assert combined_cycle_cloud_template_id
ip_camera_street_template_id = get_template_id_from_name(templates, "iotsim-ip-camera-street")
assert ip_camera_street_template_id
ip_camera_museum_template_id = get_template_id_from_name(templates, "iotsim-ip-camera-museum")
assert ip_camera_museum_template_id
stream_server_template_id = get_template_id_from_name(templates, "iotsim-stream-server")
assert stream_server_template_id
stream_consumer_template_id = get_template_id_from_name(templates, "iotsim-stream-consumer")
assert stream_consumer_template_id
debug_client_template_id = get_template_id_from_name(templates, "iotsim-debug-client")
assert debug_client_template_id
mqtt_client_t1_compromised_template_id = get_template_id_from_name(templates, "iotsim-mqtt-client-compromised-t1")
assert mqtt_client_t1_compromised_template_id
mqtt_client_t2_compromised_template_id = get_template_id_from_name(templates, "iotsim-mqtt-client-compromised-t2")
assert mqtt_client_t2_compromised_template_id
coap_server_compromised_template_id = get_template_id_from_name(templates, "iotsim-coap-server-compromised")
assert coap_server_compromised_template_id


# read project configuration file
sim_config = configparser.ConfigParser()
with open("../iot-sim.config", "r", encoding="utf-8") as cf:
    # include fake section header 'main'
    sim_config.read_string(f"[main]\n{cf.read()}")
    sim_config = sim_config["main"]


input("Open the GNS3 project GUI. Press enter to continue...")

############
# TOPOLOGY #
############
# Coordinates:
#
#            ^
#  --        | Y -    +-
#            |
#            |
#  X -       |(0,0)   X +
# <----------+---------->
#            |
#            |
#            |
#            |
#  -+        v Y +     ++

coord_rnorth = Position(1000, -1700)
coord_rwest = Position(coord_rnorth.x - project.grid_unit * 2, coord_rnorth.y + project.grid_unit * 4)
coord_reast = Position(coord_rnorth.x + project.grid_unit * 2, coord_rnorth.y + project.grid_unit * 4)

####################
# backbone routers #
####################

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
if AUTO_CONFIGURE_ROUTERS:
    for router_node, router_config in zip(backbone_routers, backbone_configs):
        print(f"Installing {router_node['name']}")
        hostname, port = get_node_telnet_host_port(server, project, router_node["node_id"])
        terminal_cmd = f"konsole -e telnet {hostname} {port}"
        start_node(server, project, router_node["node_id"])
        install_vyos_image_on_node(router_node["node_id"], hostname, port, pre_exec=terminal_cmd)
        # time to close the terminals, else Telnet throws EOF errors
        time.sleep(10)
        print(f"Configuring {router_node['name']} with {router_config}")
        start_node(server, project, router_node["node_id"])
        configure_vyos_image_on_node(router_node["node_id"], hostname, port, router_config, pre_exec=terminal_cmd)
        time.sleep(10)

#####################
# backbone switches #
#####################

coord_snorth = Position(coord_rnorth.x, coord_rnorth.y - project.grid_unit * 2)
coord_swest = Position(coord_rwest.x - project.grid_unit * 10, coord_rwest.y)
coord_seast = Position(coord_reast.x + project.grid_unit * 25, coord_reast.y)

snorth = create_node(server, project, coord_snorth.x, coord_snorth.y, switch_template_id)
swest = create_node(server, project, coord_swest.x, coord_swest.y, switch_template_id)
seast = create_node(server, project, coord_seast.x, coord_seast.y, switch_template_id)

create_link(server, project, rnorth["node_id"], 0, snorth["node_id"], 0)
create_link(server, project, rwest["node_id"], 0, swest["node_id"], 0)
create_link(server, project, reast["node_id"], 0, seast["node_id"], 0)

# west zone routers and switches
routers_west_zone = []
switches_west_zone = []
coords_west_zone = []
switch_freeport = 1
for i in [-40, -20, 0, 20]:
    coord = Position(coord_swest.x + project.grid_unit * i, coord_swest.y + project.grid_unit * 3)
    rzone = create_node(server, project, coord.x, coord.y, router_template_id)
    create_link(server, project, rzone["node_id"], 1, swest["node_id"], switch_freeport)
    switch_freeport += 1
    coord = Position(coord.x, coord.y + project.grid_unit * 2)
    szone = create_node(server, project, coord.x, coord.y, switch_template_id)
    create_link(server, project, rzone["node_id"], 0, szone["node_id"], 0)
    routers_west_zone.append(rzone)
    switches_west_zone.append(szone)
    coords_west_zone.append(coord)

# router installation and configuration
rwest_configs = [f"../router/locations/router_loc{i}.sh" for i in range(1, 5)]
if AUTO_CONFIGURE_ROUTERS:
    for router_node, router_config in zip(routers_west_zone, rwest_configs):
        print(f"Installing {router_node['name']}")
        hostname, port = get_node_telnet_host_port(server, project, router_node["node_id"])
        terminal_cmd = f"konsole -e telnet {hostname} {port}"
        start_node(server, project, router_node["node_id"])
        install_vyos_image_on_node(router_node["node_id"], hostname, port, pre_exec=terminal_cmd)
        # time to close the terminals, else Telnet throws EOF errors
        time.sleep(10)
        print(f"Configuring {router_node['name']} with {router_config}")
        start_node(server, project, router_node["node_id"])
        configure_vyos_image_on_node(router_node["node_id"], hostname, port, router_config, pre_exec=terminal_cmd)
        time.sleep(10)

# east zone routers and switches
routers_east_zone = []
switches_east_zone = []
coords_east_zone = []
switch_freeport = 1
for i in [-5, 0, 5]:
    coord = Position(coord_seast.x + project.grid_unit * i, coord_seast.y + project.grid_unit * 3)
    rzone = create_node(server, project, coord.x, coord.y, router_template_id)
    create_link(server, project, rzone["node_id"], 1, seast["node_id"], switch_freeport)
    switch_freeport += 1
    coord = Position(coord.x, coord.y + project.grid_unit * 2)
    szone = create_node(server, project, coord.x, coord.y, switch_template_id)
    create_link(server, project, rzone["node_id"], 0, szone["node_id"], 0)
    routers_east_zone.append(rzone)
    switches_east_zone.append(szone)
    coords_east_zone.append(coord)

# router installation and configuration
reast_configs = [f"../router/locations/router_loc{i}.sh" for i in range(5, 8)]
if AUTO_CONFIGURE_ROUTERS:
    for router_node, router_config in zip(routers_east_zone, reast_configs):
        print(f"Installing {router_node['name']}")
        hostname, port = get_node_telnet_host_port(server, project, router_node["node_id"])
        terminal_cmd = f"konsole -e telnet {hostname} {port}"
        start_node(server, project, router_node["node_id"])
        install_vyos_image_on_node(router_node["node_id"], hostname, port, pre_exec=terminal_cmd)
        # time to close the terminals, else Telnet throws EOF errors
        time.sleep(10)
        print(f"Configuring {router_node['name']} with {router_config}")
        start_node(server, project, router_node["node_id"])
        configure_vyos_image_on_node(router_node["node_id"], hostname, port, router_config, pre_exec=terminal_cmd)
        time.sleep(10)


lab_nameserver = sim_config["LAB_DNS_IPADDR"]


#######
# DNS #
#######

coord_cloud_snorth = Position(coord_snorth.x + project.grid_unit * 8, coord_snorth.y - project.grid_unit * 2)
cloud_snorth = create_node(server, project, coord_cloud_snorth.x, coord_cloud_snorth.y, switch_template_id)
create_link(server, project, snorth["node_id"], 1, cloud_snorth["node_id"], 0)

dns = create_node(server, project, coord_cloud_snorth.x - project.grid_unit * 1, coord_cloud_snorth.y - project.grid_unit * 2, DNS_template_id)
create_link(server, project, cloud_snorth["node_id"], 1, dns["node_id"], 0)
set_node_network_interfaces(server, project, dns["node_id"], "eth0", ipaddress.IPv4Interface(f"{lab_nameserver}/20"), "192.168.0.1", "127.0.0.1")


#######
# NTP #
#######

ntp = create_node(server, project, coord_cloud_snorth.x + project.grid_unit * 1, coord_cloud_snorth.y - project.grid_unit * 2, NTP_template_id)
create_link(server, project, cloud_snorth["node_id"], 2, ntp["node_id"], 0)
set_node_network_interfaces(server, project, ntp["node_id"], "eth0", ipaddress.IPv4Interface("192.168.0.3/20"), "192.168.0.1", lab_nameserver)


######################
# Secure MQTT broker #
######################

MQTT_CLOUD_TLS_NAME = (sim_config["MQTT_TLS_BROKER_CN"], "192.168.0.4")

mqtt_cloud_tls = create_node(server, project, coord_cloud_snorth.x + project.grid_unit * 3, coord_cloud_snorth.y - project.grid_unit * 2, mqtt_broker_tls_template_id)
create_link(server, project, cloud_snorth["node_id"], 3, mqtt_cloud_tls["node_id"], 0)
set_node_network_interfaces(server, project, mqtt_cloud_tls["node_id"], "eth0", ipaddress.IPv4Interface(f"{MQTT_CLOUD_TLS_NAME[1]}/20"), "192.168.0.1", lab_nameserver)


#########
# Mirai #
#########

mirai_cnc = create_node(server, project, coords_east_zone[0].x - project.grid_unit, coords_east_zone[0].y + project.grid_unit * 2, Mirai_cnc_template_id)
create_link(server, project, switches_east_zone[0]["node_id"], 1, mirai_cnc["node_id"], 0)
set_node_network_interfaces(server, project, mirai_cnc["node_id"], "eth0", ipaddress.IPv4Interface(f"{sim_config['MIRAI_CNC_IPADDR']}/24"), "192.168.33.1", lab_nameserver)

mirai_scan_listener = create_node(server, project, coords_east_zone[0].x + project.grid_unit, coords_east_zone[0].y + project.grid_unit * 2, Mirai_scan_listener_template_id)
create_link(server, project, switches_east_zone[0]["node_id"], 2, mirai_scan_listener["node_id"], 0)
set_node_network_interfaces(server, project, mirai_scan_listener["node_id"], "eth0", ipaddress.IPv4Interface(f"{sim_config['MIRAI_REPORT_IPADDR']}/24"), "192.168.33.1", lab_nameserver)

mirai_loader = create_node(server, project, coords_east_zone[0].x - project.grid_unit, coords_east_zone[0].y + project.grid_unit * 3, Mirai_loader_template_id)
create_link(server, project, switches_east_zone[0]["node_id"], 3, mirai_loader["node_id"], 0)
set_node_network_interfaces(server, project, mirai_loader["node_id"], "eth0", ipaddress.IPv4Interface("192.168.33.12/24"), "192.168.33.1", lab_nameserver)

mirai_wget_loader = create_node(server, project, coords_east_zone[0].x + project.grid_unit, coords_east_zone[0].y + project.grid_unit * 3, Mirai_wget_loader_template_id)
create_link(server, project, switches_east_zone[0]["node_id"], 4, mirai_wget_loader["node_id"], 0)
set_node_network_interfaces(server, project, mirai_wget_loader["node_id"], "eth0", ipaddress.IPv4Interface(f"{sim_config['MIRAI_WGET_LOADER_IPADDR']}/24"), "192.168.33.1", lab_nameserver)

mirai_bot = create_node(server, project, coord_cloud_snorth.x + project.grid_unit * 5, coord_cloud_snorth.y - project.grid_unit * 2, Mirai_bot_template_id)
create_link(server, project, cloud_snorth["node_id"], 4, mirai_bot["node_id"], 0)
set_node_network_interfaces(server, project, mirai_bot["node_id"], "eth0", ipaddress.IPv4Interface("192.168.0.100/20"), "192.168.0.1", lab_nameserver)


##########
# Merlin #
##########

merlin_cnc = create_node(server, project, coords_east_zone[1].x, coords_east_zone[1].y + project.grid_unit * 2, Merlin_template_id)
create_link(server, project, switches_east_zone[1]["node_id"], 1, merlin_cnc["node_id"], 0)
set_node_network_interfaces(server, project, merlin_cnc["node_id"], "eth0", ipaddress.IPv4Interface("192.168.34.10/24"), "192.168.34.1", lab_nameserver)


###################################
# Scanner and mqtt / coap attacks #
###################################

scanner = create_node(server, project, coords_east_zone[2].x - project.grid_unit, coords_east_zone[2].y + project.grid_unit * 2, scanner_template_id)
create_link(server, project, switches_east_zone[2]["node_id"], 1, scanner["node_id"], 0)
set_node_network_interfaces(server, project, scanner["node_id"], "eth0", ipaddress.IPv4Interface("192.168.35.10/24"), "192.168.35.1", lab_nameserver)

amplification_coap = create_node(server, project, coords_east_zone[2].x + project.grid_unit, coords_east_zone[2].y + project.grid_unit * 2, amplification_coap_template_id)
create_link(server, project, switches_east_zone[2]["node_id"], 2, amplification_coap["node_id"], 0)
set_node_network_interfaces(server, project, amplification_coap["node_id"], "eth0", ipaddress.IPv4Interface("192.168.35.11/24"), "192.168.35.1", lab_nameserver)

mqtt_attacks = create_node(server, project, coords_east_zone[2].x - project.grid_unit, coords_east_zone[2].y + project.grid_unit * 3, mqtt_attacks_template_id)
create_link(server, project, switches_east_zone[2]["node_id"], 3, mqtt_attacks["node_id"], 0)
set_node_network_interfaces(server, project, mqtt_attacks["node_id"], "eth0", ipaddress.IPv4Interface("192.168.35.12/24"), "192.168.35.1", lab_nameserver)

metasploit = create_node(server, project, coords_east_zone[2].x + project.grid_unit, coords_east_zone[2].y + project.grid_unit * 3, metasploit_template_id)
create_link(server, project, switches_east_zone[2]["node_id"], 4, metasploit["node_id"], 0)
set_node_network_interfaces(server, project, metasploit["node_id"], "eth0", ipaddress.IPv4Interface("192.168.35.13/24"), "192.168.35.1", lab_nameserver)


########
# Labs #
########

LABS_BROKER_PLAIN_NAME = (f"broker.labs.{sim_config['LOCAL_DOMAIN']}", "192.168.4.2")

coord_labs_snorth = Position(coord_snorth.x + project.grid_unit * 4, coord_snorth.y - project.grid_unit * 2)
labs_snorth = create_node(server, project, coord_labs_snorth.x, coord_labs_snorth.y, switch_template_id)
create_link(server, project, snorth["node_id"], 2, labs_snorth["node_id"], 0)

labs_clus_comb_plain = create_cluster_of_nodes(server, project, 10, coords_west_zone[3].x - project.grid_unit * 5, coords_west_zone[3].y + project.grid_unit * 2, 5,
                                               switch_template_id, combined_cycle_template_id, switches_west_zone[3]["node_id"], 1,
                                               ipaddress.IPv4Interface("192.168.20.10/24"), "192.168.20.1", lab_nameserver, 1.5)

labs_comb_cloud_plain = create_node(server, project, coord_labs_snorth.x + project.grid_unit * 1, coord_labs_snorth.y - project.grid_unit * 2, combined_cycle_cloud_template_id)
create_link(server, project, labs_snorth["node_id"], 1, labs_comb_cloud_plain["node_id"], 0)
set_node_network_interfaces(server, project, labs_comb_cloud_plain["node_id"], "eth0", ipaddress.IPv4Interface("192.168.4.1/20"), "192.168.0.1", lab_nameserver)
env = environment_string_to_dict(get_docker_node_environment(server, project, labs_comb_cloud_plain["node_id"]))
env["COAP_ADDR_LIST"] = "192.168.20.10-192.168.20.19"
update_docker_node_environment(server, project, labs_comb_cloud_plain["node_id"], environment_dict_to_string(env))

labs_clus_comb_dtls = create_cluster_of_nodes(server, project, 5, coords_west_zone[3].x - project.grid_unit * 5, coords_west_zone[3].y + project.grid_unit * 7, 5,
                                              switch_template_id, combined_cycle_tls_template_id, switches_west_zone[3]["node_id"], 2,
                                              ipaddress.IPv4Interface("192.168.20.20/24"), "192.168.20.1", lab_nameserver, 1.5)

labs_comb_cloud_dtls = create_node(server, project, coord_labs_snorth.x + project.grid_unit * 1, coord_labs_snorth.y - project.grid_unit * 4, combined_cycle_cloud_template_id)
create_link(server, project, labs_snorth["node_id"], 2, labs_comb_cloud_dtls["node_id"], 0)
set_node_network_interfaces(server, project, labs_comb_cloud_dtls["node_id"], "eth0", ipaddress.IPv4Interface("192.168.4.3/20"), "192.168.0.1", lab_nameserver)
env = environment_string_to_dict(get_docker_node_environment(server, project, labs_comb_cloud_dtls["node_id"]))
env["COAP_ADDR_LIST"] = "192.168.20.20-192.168.20.24"
env["PSK"] = "True"
update_docker_node_environment(server, project, labs_comb_cloud_dtls["node_id"], environment_dict_to_string(env))

labs_mqtt_cloud_plain = create_node(server, project, coord_labs_snorth.x - project.grid_unit * 1, coord_labs_snorth.y - project.grid_unit * 2, mqtt_broker_1_6_template_id)
create_link(server, project, labs_snorth["node_id"], 3, labs_mqtt_cloud_plain["node_id"], 0)
set_node_network_interfaces(server, project, labs_mqtt_cloud_plain["node_id"], "eth0", ipaddress.IPv4Interface(f"{LABS_BROKER_PLAIN_NAME[1]}/20"), "192.168.0.1", lab_nameserver)

labs_clus_hydr_plain = create_cluster_of_nodes(server, project, 10, coords_west_zone[3].x + project.grid_unit * 5, coords_west_zone[3].y + project.grid_unit * 2, 5,
                                               switch_template_id, hydraulic_system_template_id, switches_west_zone[3]["node_id"], 3,
                                               ipaddress.IPv4Interface("192.168.20.30/24"), "192.168.20.1", lab_nameserver, 1.5)
for d in labs_clus_hydr_plain[1]:
    env = environment_string_to_dict(get_docker_node_environment(server, project, d["node_id"]))
    env["MQTT_BROKER_ADDR"] = LABS_BROKER_PLAIN_NAME[0]
    update_docker_node_environment(server, project, d["node_id"], environment_dict_to_string(env))

labs_clus_hydr_tls = create_cluster_of_nodes(server, project, 5, coords_west_zone[3].x + project.grid_unit * 5, coords_west_zone[3].y + project.grid_unit * 7, 5,
                                             switch_template_id, hydraulic_system_template_id, switches_west_zone[3]["node_id"], 4,
                                             ipaddress.IPv4Interface("192.168.20.40/24"), "192.168.20.1", lab_nameserver, 1.5)
for d in labs_clus_hydr_tls[1]:
    env = environment_string_to_dict(get_docker_node_environment(server, project, d["node_id"]))
    env["MQTT_BROKER_ADDR"] = MQTT_CLOUD_TLS_NAME[0]
    env["TLS"] = "True"
    update_docker_node_environment(server, project, d["node_id"], environment_dict_to_string(env))


#########
# Steel #
#########

STEEL_BROKER_AUTH_NAME = (f"broker.steel.{sim_config['LOCAL_DOMAIN']}", "192.168.3.1")

coord_steel_snorth = Position(coord_snorth.x + project.grid_unit * 0, coord_snorth.y - project.grid_unit * 2)
steel_snorth = create_node(server, project, coord_steel_snorth.x, coord_steel_snorth.y, switch_template_id)
create_link(server, project, snorth["node_id"], 3, steel_snorth["node_id"], 0)

steel_mqtt_cloud_auth = create_node(server, project, coord_steel_snorth.x, coord_steel_snorth.y - project.grid_unit * 2, mqtt_broker_1_6_auth_template_id)
create_link(server, project, steel_snorth["node_id"], 1, steel_mqtt_cloud_auth["node_id"], 0)
set_node_network_interfaces(server, project, steel_mqtt_cloud_auth["node_id"], "eth0", ipaddress.IPv4Interface(f"{STEEL_BROKER_AUTH_NAME[1]}/20"), "192.168.0.1", lab_nameserver)


steel_clus_cooler_plain = create_cluster_of_nodes(server, project, 10, coords_west_zone[2].x - project.grid_unit * 5, coords_west_zone[2].y + project.grid_unit * 2, 5,
                                                  switch_template_id, cooler_motor_template_id, switches_west_zone[2]["node_id"], 1,
                                                  ipaddress.IPv4Interface("192.168.19.10/24"), "192.168.19.1", lab_nameserver, 1.5)
for d in steel_clus_cooler_plain[1]:
    env = environment_string_to_dict(get_docker_node_environment(server, project, d["node_id"]))
    env["MQTT_BROKER_ADDR"] = STEEL_BROKER_AUTH_NAME[0]
    # See the file Dockerfiles/iot/mqtt_broker/mosquitto_1.6.auth.passwd
    env["MQTT_AUTH"] = "admin:adminpass"
    update_docker_node_environment(server, project, d["node_id"], environment_dict_to_string(env))

steel_clus_pred_plain = create_cluster_of_nodes(server, project, 10, coords_west_zone[2].x + project.grid_unit * 5, coords_west_zone[2].y + project.grid_unit * 2, 5,
                                                switch_template_id, predictive_maintenance_template_id, switches_west_zone[2]["node_id"], 2,
                                                ipaddress.IPv4Interface("192.168.19.20/24"), "192.168.19.1", lab_nameserver, 1.5)
for d in steel_clus_pred_plain[1]:
    env = environment_string_to_dict(get_docker_node_environment(server, project, d["node_id"]))
    env["MQTT_BROKER_ADDR"] = STEEL_BROKER_AUTH_NAME[0]
    # See the file Dockerfiles/iot/mqtt_broker/mosquitto_1.6.auth.passwd
    env["MQTT_AUTH"] = "production:passw0rd"
    update_docker_node_environment(server, project, d["node_id"], environment_dict_to_string(env))

steel_clus_cooler_tls = create_cluster_of_nodes(server, project, 5, coords_west_zone[2].x - project.grid_unit * 5, coords_west_zone[2].y + project.grid_unit * 7, 5,
                                                switch_template_id, cooler_motor_template_id, switches_west_zone[2]["node_id"], 3,
                                                ipaddress.IPv4Interface("192.168.19.30/24"), "192.168.19.1", lab_nameserver, 1.5)
for d in steel_clus_cooler_tls[1]:
    env = environment_string_to_dict(get_docker_node_environment(server, project, d["node_id"]))
    env["MQTT_BROKER_ADDR"] = MQTT_CLOUD_TLS_NAME[0]
    env["TLS"] = "True"
    update_docker_node_environment(server, project, d["node_id"], environment_dict_to_string(env))

steel_clus_pred_tls = create_cluster_of_nodes(server, project, 5, coords_west_zone[2].x + project.grid_unit * 5, coords_west_zone[2].y + project.grid_unit * 7, 5,
                                              switch_template_id, predictive_maintenance_template_id, switches_west_zone[2]["node_id"], 4,
                                              ipaddress.IPv4Interface("192.168.19.40/24"), "192.168.19.1", lab_nameserver, 1.5)
for d in steel_clus_pred_tls[1]:
    env = environment_string_to_dict(get_docker_node_environment(server, project, d["node_id"]))
    env["MQTT_BROKER_ADDR"] = MQTT_CLOUD_TLS_NAME[0]
    env["TLS"] = "True"
    update_docker_node_environment(server, project, d["node_id"], environment_dict_to_string(env))


################
# Neighborhood #
################

NEIGH_BROKER_PLAIN_NAME = (f"broker.neigh.{sim_config['LOCAL_DOMAIN']}", "192.168.2.1")
NEIGH_STREAMSERVER_NAME = (f"ipcam.neigh.{sim_config['LOCAL_DOMAIN']}", "192.168.2.2")

coord_neigh_snorth = Position(coord_snorth.x + project.grid_unit * -4, coord_snorth.y - project.grid_unit * 2)
neigh_snorth = create_node(server, project, coord_neigh_snorth.x, coord_neigh_snorth.y, switch_template_id)
create_link(server, project, snorth["node_id"], 4, neigh_snorth["node_id"], 0)

neigh_mqtt_cloud_plain = create_node(server, project, coord_neigh_snorth.x + project.grid_unit * 1, coord_neigh_snorth.y - project.grid_unit * 2, mqtt_broker_1_6_template_id)
create_link(server, project, neigh_snorth["node_id"], 1, neigh_mqtt_cloud_plain["node_id"], 0)
set_node_network_interfaces(server, project, neigh_mqtt_cloud_plain["node_id"], "eth0", ipaddress.IPv4Interface(f"{NEIGH_BROKER_PLAIN_NAME[1]}/20"), "192.168.0.1", lab_nameserver)

neigh_stream_cloud = create_node(server, project, coord_neigh_snorth.x - project.grid_unit * 1, coord_neigh_snorth.y - project.grid_unit * 2, stream_server_template_id)
create_link(server, project, neigh_snorth["node_id"], 2, neigh_stream_cloud["node_id"], 0)
set_node_network_interfaces(server, project, neigh_stream_cloud["node_id"], "eth0", ipaddress.IPv4Interface(f"{NEIGH_STREAMSERVER_NAME[1]}/20"), "192.168.0.1", lab_nameserver)

neigh_clus_domotic_plain = create_cluster_of_nodes(server, project, 5, coords_west_zone[1].x - project.grid_unit * 5, coords_west_zone[1].y + project.grid_unit * 2, 5,
                                                   switch_template_id, domotic_monitor_template_id, switches_west_zone[1]["node_id"], 1,
                                                   ipaddress.IPv4Interface("192.168.18.10/24"), "192.168.18.1", lab_nameserver, 1.5)
for d in neigh_clus_domotic_plain[1]:
    env = environment_string_to_dict(get_docker_node_environment(server, project, d["node_id"]))
    # TODO. change dataset env.
    env["MQTT_BROKER_ADDR"] = NEIGH_BROKER_PLAIN_NAME[0]
    update_docker_node_environment(server, project, d["node_id"], environment_dict_to_string(env))

neigh_clus_ipcam = create_cluster_of_nodes(server, project, 2, coords_west_zone[1].x + project.grid_unit * 5, coords_west_zone[1].y + project.grid_unit * 2, 2,
                                           switch_template_id, ip_camera_street_template_id, switches_west_zone[1]["node_id"], 2,
                                           ipaddress.IPv4Interface("192.168.18.15/24"), "192.168.18.1", lab_nameserver, 1.5)
for d in neigh_clus_ipcam[1]:
    env = environment_string_to_dict(get_docker_node_environment(server, project, d["node_id"]))
    env["STREAM_SERVER_ADDR"] = NEIGH_STREAMSERVER_NAME[0]
    env["STREAM_NAME"] = d["name"]
    update_docker_node_environment(server, project, d["node_id"], environment_dict_to_string(env))

neigh_clus_air_plain = create_cluster_of_nodes(server, project, 1, coords_west_zone[1].x + project.grid_unit * 5, coords_west_zone[1].y + project.grid_unit * 7, 1,
                                               switch_template_id, air_quality_template_id, switches_west_zone[1]["node_id"], 3,
                                               ipaddress.IPv4Interface("192.168.18.17/24"), "192.168.18.1", lab_nameserver, 1.5)
for d in neigh_clus_air_plain[1]:
    env = environment_string_to_dict(get_docker_node_environment(server, project, d["node_id"]))
    env["MQTT_BROKER_ADDR"] = NEIGH_BROKER_PLAIN_NAME[0]
    update_docker_node_environment(server, project, d["node_id"], environment_dict_to_string(env))

neigh_clus_city = create_cluster_of_nodes(server, project, 1, coords_west_zone[1].x + project.grid_unit * 5, coords_west_zone[1].y + project.grid_unit * 12, 1,
                                          switch_template_id, city_power_template_id, switches_west_zone[1]["node_id"], 4,
                                          ipaddress.IPv4Interface("192.168.18.18/24"), "192.168.18.1", lab_nameserver, 1.5)
neigh_city_cloud = create_node(server, project, coord_neigh_snorth.x + project.grid_unit * 1, coord_neigh_snorth.y - project.grid_unit * 4, city_power_cloud_template_id)
create_link(server, project, neigh_snorth["node_id"], 3, neigh_city_cloud["node_id"], 0)
set_node_network_interfaces(server, project, neigh_city_cloud["node_id"], "eth0", ipaddress.IPv4Interface("192.168.2.3/20"), "192.168.0.1", lab_nameserver)
env = environment_string_to_dict(get_docker_node_environment(server, project, neigh_city_cloud["node_id"]))
env["COAP_ADDR_LIST"] = "192.168.18.18"
update_docker_node_environment(server, project, neigh_city_cloud["node_id"], environment_dict_to_string(env))


##########
# Museum #
##########

MUSEUM_BROKER_PLAIN_NAME = (f"broker.museum.{sim_config['LOCAL_DOMAIN']}", "192.168.1.1")
MUSEUM_STREAMSERVER_NAME = (f"ipcam.museum.{sim_config['LOCAL_DOMAIN']}", "192.168.1.2")

coord_museum_snorth = Position(coord_snorth.x + project.grid_unit * -8, coord_snorth.y - project.grid_unit * 2)
museum_snorth = create_node(server, project, coord_museum_snorth.x, coord_museum_snorth.y, switch_template_id)
create_link(server, project, snorth["node_id"], 5, museum_snorth["node_id"], 0)

museum_mqtt_cloud_plain = create_node(server, project, coord_museum_snorth.x + project.grid_unit * 1, coord_museum_snorth.y - project.grid_unit * 2, mqtt_broker_1_6_template_id)
create_link(server, project, museum_snorth["node_id"], 1, museum_mqtt_cloud_plain["node_id"], 0)
set_node_network_interfaces(server, project, museum_mqtt_cloud_plain["node_id"], "eth0", ipaddress.IPv4Interface(f"{MUSEUM_BROKER_PLAIN_NAME[1]}/20"), "192.168.0.1", lab_nameserver)

museum_stream_cloud = create_node(server, project, coord_museum_snorth.x - project.grid_unit * 1, coord_museum_snorth.y - project.grid_unit * 2, stream_server_template_id)
create_link(server, project, museum_snorth["node_id"], 2, museum_stream_cloud["node_id"], 0)
set_node_network_interfaces(server, project, museum_stream_cloud["node_id"], "eth0", ipaddress.IPv4Interface(f"{MUSEUM_STREAMSERVER_NAME[1]}/20"), "192.168.0.1", lab_nameserver)

museum_clus_building_plain = create_cluster_of_nodes(server, project, 5, coords_west_zone[0].x - project.grid_unit * 5, coords_west_zone[0].y + project.grid_unit * 2, 5,
                                                     switch_template_id, building_monitor_template_id, switches_west_zone[0]["node_id"], 1,
                                                     ipaddress.IPv4Interface("192.168.17.10/24"), "192.168.17.1", lab_nameserver, 1.5)
for d in museum_clus_building_plain[1]:
    env = environment_string_to_dict(get_docker_node_environment(server, project, d["node_id"]))
    env["MQTT_BROKER_ADDR"] = MUSEUM_BROKER_PLAIN_NAME[0]
    update_docker_node_environment(server, project, d["node_id"], environment_dict_to_string(env))

museum_clus_ipcam = create_cluster_of_nodes(server, project, 2, coords_west_zone[0].x + project.grid_unit * 5, coords_west_zone[0].y + project.grid_unit * 2, 2,
                                            switch_template_id, ip_camera_museum_template_id, switches_west_zone[0]["node_id"], 2,
                                            ipaddress.IPv4Interface("192.168.17.15/24"), "192.168.17.1", lab_nameserver, 1.5)
for d in museum_clus_ipcam[1]:
    env = environment_string_to_dict(get_docker_node_environment(server, project, d["node_id"]))
    env["STREAM_SERVER_ADDR"] = MUSEUM_STREAMSERVER_NAME[0]
    env["STREAM_NAME"] = d["name"]
    update_docker_node_environment(server, project, d["node_id"], environment_dict_to_string(env))

museum_clus_ipconsum = create_cluster_of_nodes(server, project, 2, coords_west_zone[0].x + project.grid_unit * 5, coords_west_zone[0].y + project.grid_unit * 7, 2,
                                               switch_template_id, stream_consumer_template_id, switches_west_zone[0]["node_id"], 3,
                                               ipaddress.IPv4Interface("192.168.17.17/24"), "192.168.17.1", lab_nameserver, 1.5)
for i, d in enumerate(museum_clus_ipconsum[1]):
    env = environment_string_to_dict(get_docker_node_environment(server, project, d["node_id"]))
    env["STREAM_SERVER_ADDR"] = MUSEUM_STREAMSERVER_NAME[0]
    env["STREAM_NAME"] = museum_clus_ipcam[1][i]["name"]
    update_docker_node_environment(server, project, d["node_id"], environment_dict_to_string(env))




EXTRA_HOSTS = {LABS_BROKER_PLAIN_NAME[0]: LABS_BROKER_PLAIN_NAME[1],
               STEEL_BROKER_AUTH_NAME[0]: STEEL_BROKER_AUTH_NAME[1],
               NEIGH_BROKER_PLAIN_NAME[0]: NEIGH_BROKER_PLAIN_NAME[1],
               NEIGH_STREAMSERVER_NAME[0]: NEIGH_STREAMSERVER_NAME[1],
               MUSEUM_BROKER_PLAIN_NAME[0]: MUSEUM_BROKER_PLAIN_NAME[1],
               MUSEUM_STREAMSERVER_NAME[0]: MUSEUM_STREAMSERVER_NAME[1],
               MQTT_CLOUD_TLS_NAME[0]: MQTT_CLOUD_TLS_NAME[1]}

update_docker_node_extrahosts(server, project, dns["node_id"], extrahosts_dict_to_string(EXTRA_HOSTS))

check_ipaddrs(server, project)
