import time
import docker
from telnetlib import Telnet
from gns3utils import *


def start_merlin_cnc_listener(hostname: str, telnet_port: int, sleep_time: float = 2) -> None:
    """ Start merlin listener.
    In the Merlin interactive console run:

    - listeners
    - use https
    - set Interface 0.0.0.0
    - start
    """

    with Telnet(hostname, telnet_port) as tn:
        print(tn.read_very_eager().decode("utf-8"))

        tn.write(b"listeners\n")
        time.sleep(sleep_time)
        print(tn.read_very_eager().decode("utf-8"))

        tn.write(b"use https\n")
        time.sleep(sleep_time)
        print(tn.read_very_eager().decode("utf-8"))

        tn.write(b"set Interface 0.0.0.0\n")
        time.sleep(sleep_time)
        print(tn.read_very_eager().decode("utf-8"))

        tn.write(b"start\n")
        time.sleep(sleep_time)
        print(tn.read_very_eager().decode("utf-8"))

        tn.write(b"info\n")
        time.sleep(sleep_time * 3)
        print(tn.read_very_eager().decode("utf-8"))


def exec_merlin_agent(merlin_bot_container, cnc_addr: str, cnc_port: int, cnc_sleep: int):
    """ Start merlin agent bot
    Example: '/opt/merlin/merlinAgent-Linux-x64 -url https://192.168.0.100:443 -sleep 20s'
    """
    merlin_bot_container.exec_run(f"/opt/merlin/merlinAgent-Linux-x64 -url https://{cnc_addr}:{cnc_port} -sleep {cnc_sleep}s", detach=True)
    merlin_bot_container.top()



PROJECT_NAME = "iot_sim"
check_local_gns3_config()
server = Server(*read_local_gns3_config())
project = get_project_by_name(server, PROJECT_NAME)

docker_client = docker.from_env()
docker_client.ping()

all_iot = get_nodes_id_by_name_regexp(server, project, re.compile("iotsim-.*", re.IGNORECASE))
merlin_cnc = next(filter(lambda i: i.name == "iotsim-merlin-cnc-1", all_iot))
merlin_cnc_h, merlin_cnc_p = get_node_telnet_host_port(server, project, merlin_cnc.id)

start_merlin_cnc_listener(merlin_cnc_h, merlin_cnc_p)
