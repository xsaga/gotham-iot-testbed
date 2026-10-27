"""Run the konro scenario (topology created by create_topology_konro.py).

1. Starts routers, switches, cloud services, sensors, edge workers and Mirai nodes.
2. Makes a subset of nodes vulnerable to Mirai (BusyBox telnetd + weak credentials).
3. Optionally starts the Mirai bot, which will really compromise the vulnerable nodes.

Run from the src/ directory:  python3 run_scenario_konro.py [--mirai]
"""

import random
import re
import sys
import time

import docker

from gns3utils import *

# Copied from run_mirai.py (importing it would run that script against gotham_scenario).
# Subset of the root passwords in Mirai's brute-force table.
MIRAI_ROOT_PASSWORDS = ["xc3511", "vizxv", "admin", "888888", "xmhdipc", "default", "juantech",
                        "123456", "54321", "root", "12345", "pass", "1111", "password", "1234"]


def make_node_vulnerable_to_mirai(node_container, username, password):
    """BusyBox login shell + weak password + telnet server (same as run_mirai.py)."""
    node_container.exec_run("chsh --shell /bin/busyboxsh")
    node_container.exec_run(f"sh -c 'echo {username}:{password} | chpasswd'")
    node_container.exec_run("busybox telnetd")


def exec_mirai_bot(mirai_bot_container):
    mirai_bot_container.exec_run("./mirai.dbg", detach=True)

PROJECT_NAME = "konro_scenario"

# Nodes that Mirai will be able to compromise.
# Keep at least one clean worker per zone, so the policy always has a safe target.
VULNERABLE_NODES = ["iotsim-edge-worker-1",          # zone A worker
                    "iotsim-edge-worker-3",          # zone B worker
                    "iotsim-domotic-monitor-3",      # zone A sensor
                    "iotsim-hydraulic-system-3"]     # zone B sensor

START_MIRAI = "--mirai" in sys.argv

check_resources()
check_local_gns3_config()
server = Server(*read_local_gns3_config())
check_server_version(server)

project = get_project_by_name(server, PROJECT_NAME)
if not project:
    print(f"Project {PROJECT_NAME} does not exist! Run create_topology_konro.py first.")
    sys.exit(1)
open_project_if_closed(server, project)

check_ipaddrs(server, project)

docker_client = docker.from_env()
docker_client.ping()

#########
# Start #
#########

start_all_routers(server, project, sleeptime=30)
start_all_switches(server, project)
time.sleep(10)  # let the switches create their bridges before the devices start

all_iot = get_nodes_id_by_name_regexp(server, project, re.compile("iotsim-.*", re.IGNORECASE))


def start_group(pattern: str):
    for n in sorted(filter(lambda n: re.search(pattern, n.name), all_iot), key=lambda x: x.name):
        print(f"Starting {n.name}")
        start_node(server, project, n.id)
        time.sleep(0.2)


start_group(r"dns|ntp")                 # general services first
time.sleep(5)
start_group(r"broker|mirai")            # broker and Mirai infrastructure
time.sleep(5)
start_group(r"domotic|hydraulic")       # sensors
start_group(r"edge-worker")             # compute nodes

# limit the Mirai bot resources, as in run_scenario_gotham.py
mirai_bot = next(filter(lambda i: i.name == "iotsim-mirai-bot-1", all_iot))
container_mirai_bot = docker_client.containers.get(get_node_docker_container_id(server, project, mirai_bot.id))
container_mirai_bot.update(mem_limit="512m", memswap_limit=-1, cpuset_cpus="0", cpu_period=100000, cpu_quota=10000)

##########################
# Vulnerable nodes setup #
##########################

print("\nMaking nodes vulnerable to Mirai:")
for name in VULNERABLE_NODES:
    node = next((x for x in all_iot if x.name == name), None)
    if node is None:
        print(f"  {name}: not found, skipped")
        continue
    container = docker_client.containers.get(get_node_docker_container_id(server, project, node.id))
    password = random.choice(MIRAI_ROOT_PASSWORDS)
    make_node_vulnerable_to_mirai(container, "root", password)
    print(f"  {name}: root / {password}")

if START_MIRAI:
    print("\nStarting the Mirai bot")
    exec_mirai_bot(container_mirai_bot)
else:
    print("\nMirai bot NOT started. Re-run with --mirai to start the infection.")
