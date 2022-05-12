import random
import docker
from gns3utils import *

# After run_scenaio_iotsim.py
# TODO. Log timestamps.

MIRAI_BRUTEFORCE_USER_PASS = {"666666": ["666666"],
                              "888888": ["888888"],
                              "Administrator": ["admin"],
                              "admin": [# "",
                                        "1111",
                                        "1111111",
                                        "1234",
                                        "1234",
                                        "12345",
                                        "123456",
                                        "54321",
                                        "7ujMko0admin",
                                        "admin",
                                        "admin1234",
                                        "meinsm",
                                        "pass",
                                        "password",
                                        "smcadmin"],
                              "admin1": ["password"],
                              "administrator": ["1234"],
                              "guest": ["12345",
                                        "12345",
                                        "guest"],
                              "mother": ["fucker"],
                              "root": [# "",
                                       "00000000",
                                       "1111",
                                       "1234",
                                       "12345",
                                       "123456",
                                       "54321",
                                       "666666",
                                       "7ujMko0admin",
                                       "7ujMko0vizxv",
                                       "888888",
                                       "Zte521",
                                       "admin",
                                       "anko",
                                       "default",
                                       "dreambox",
                                       "hi3518",
                                       "ikwb",
                                       "juantech",
                                       "jvbzd",
                                       "klv123",
                                       "klv1234",
                                       "pass",
                                       "password",
                                       "realtek",
                                       "root",
                                       "system",
                                       "user",
                                       "vizxv",
                                       "xc3511",
                                       "xmhdipc",
                                       "zlxx."],
                              "service": ["service"],
                              "supervisor": ["supervisor"],
                              "support": ["support"],
                              "tech": ["tech"],
                              "ubnt": ["ubnt"],
                              "user": ["user"]}


def make_node_vulnerable_to_mirai(node_container, username, password):
    # set login shell to busybox sh. '/bin/busyboxsh' created at the Dockerfile.
    node_container.exec_run("chsh --shell /bin/busyboxsh")
    # set user password
    node_container.exec_run(f"sh -c 'echo {username}:{password} | chpasswd'")
    # start telnet server
    node_container.exec_run("busybox telnetd")


def exec_mirai_bot(mirai_bot_container):
    mirai_bot_container.exec_run("./mirai.dbg", detach=True)
    mirai_bot_container.top()


PROJECT_NAME = "iot_sim"
check_local_gns3_config()
server = Server(*read_local_gns3_config())
project = get_project_by_name(server, PROJECT_NAME)

docker_client = docker.from_env()
docker_client.ping()

all_iot = get_nodes_id_by_name_regexp(server, project, re.compile("iotsim-.*", re.IGNORECASE))
mirai_bot = next(filter(lambda i: i.name == "iotsim-mirai-bot-1", all_iot))
container_mirai_bot = docker_client.containers.get(get_node_docker_container_id(server, project, mirai_bot.id))


# Prepare devices

vulnerable_devices = ["iotsim-building-monitor-5", "iotsim-ip-camera-museum-2",
                      "iotsim-domotic-monitor-5", "iotsim-ip-camera-street-2",
                      *[f"iotsim-cooler-motor-{i}" for i in range(1, 5+1)],
                      *[f"iotsim-predictive-maintenance-{i}" for i in range(1, 5+1)],
                      *[f"iotsim-combined-cycle-{i}" for i in range(1, 5+1)],
                      *[f"iotsim-hydraulic-system-{i}" for i in range(1, 5+1)]]

for vd in vulnerable_devices:
    node = next(filter(lambda x: x.name == vd, all_iot))
    container = docker_client.containers.get(get_node_docker_container_id(server, project, node.id))
    username = "root"
    password = random.choice(MIRAI_BRUTEFORCE_USER_PASS[username])
    print(node.name, username, password)
    make_node_vulnerable_to_mirai(container, username, password)

exec_mirai_bot(container_mirai_bot)
