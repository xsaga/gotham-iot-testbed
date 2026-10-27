"""Dispatcher of the sensitive applications (konro scenario).

Launches, finds, stops and moves the sensitive applications on the edge workers
of the konro_scenario project, and registers them in Konro.

It follows the same style as the other Gotham scripts in this folder:
  - configuration as constants at the top of the file (as in run_scenario_gotham.py / run_mirai.py);
  - GNS3 access through gns3utils (Server, get_project_by_name, get_nodes_id_by_name_regexp,
    get_node_docker_container_id), exactly as in run_scenario_gotham.py;
  - Docker access through the docker SDK and container.exec_run(), as in run_mirai.py
    (make_node_vulnerable_to_mirai, exec_mirai_bot);
  - HTTP calls with requests + json.dumps + raise_for_status(), as in gns3utils.py.

Usage (from the src/ directory, with the venv active):
    python3 dispatcher.py launch-all              # start every task of TASKS on its initial node
    python3 dispatcher.py launch  T1 [NODE]       # start one task (on NODE or on its initial node)
    python3 dispatcher.py kill    T1              # stop a task wherever it is running
    python3 dispatcher.py migrate T1 NODE         # kill & restart a task on another node
    python3 dispatcher.py status                  # where every task is running
"""

import io
import json
import re
import sys
import tarfile
import time

from pathlib import Path

import docker
import requests

from gns3utils import *

PROJECT_NAME = "konro_scenario"
KONRO_ADDR = "http://localhost:8080"
APP_PATH = Path(__file__).resolve().parent.parent / "tasks" / "sensitive_task.py"
APP_DIR_IN_WORKER = "/tasks"
WORKERS_PATTERN = re.compile("iotsim-edge-worker-.*", re.IGNORECASE)

# Sensitive applications of the scenario, in the same spirit as VULNERABLE_NODES in run_mirai.py.
# "node" is the worker where the task is started by launch-all.
TASKS = {"T1": {"node": "iotsim-edge-worker-1",
                "sensitive": True,
                "env": {"SOURCES": "iotsim-domotic-monitor-1,iotsim-domotic-monitor-2",
                        "DURATION": 0,
                        "WORK": 10000}},
         "T2": {"node": "iotsim-edge-worker-3",
                "sensitive": True,
                "env": {"SOURCES": "iotsim-hydraulic-system-1,iotsim-hydraulic-system-3",
                        "DURATION": 0,
                        "WORK": 10000}},
         "T3": {"node": "iotsim-edge-worker-2",
                "sensitive": False,
                "env": {"SOURCES": "iotsim-domotic-monitor-3",
                        "DURATION": 300,
                        "WORK": 5000}}}

# Common environment of every task (same variables as the Gotham MQTT devices).
COMMON_ENV = {"MQTT_BROKER_ADDR": "broker.city.lab",
              "REPORT_TIME": 10}


##################
# Docker helpers #
##################

def get_node_container(server: Server, project: Project, docker_client, node_name: str):
    """Docker container of a GNS3 node, given the node name (e.g. iotsim-edge-worker-2)."""
    nodes = get_nodes_id_by_name_regexp(server, project, re.compile(re.escape(node_name) + "$"))
    if not nodes:
        raise ValueError(f"Node {node_name} not found in project {project.name}")
    return docker_client.containers.get(get_node_docker_container_id(server, project, nodes[0].id))


def copy_app_to_container(container, app_path: Path, dest_dir: str) -> None:
    """Copy the application file into the container (equivalent to `docker cp')."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tar:
        tar.add(str(app_path), arcname=app_path.name)
    container.exec_run(f"mkdir -p {dest_dir}")
    container.put_archive(dest_dir, buf.getvalue())


def task_cmdline(task_id: str) -> str:
    """Command line that identifies a task process inside a worker."""
    return f"python3 {APP_DIR_IN_WORKER}/{APP_PATH.name} {task_id}"


def get_task_host_pid(container, task_id: str, attempts: int = 10, wait: float = 0.5) -> Optional[int]:
    """PID (in the host namespace) of the task process, using `docker top'."""
    for _ in range(attempts):
        for pid, args in container.top(ps_args="-eo pid,args")["Processes"]:
            if args.strip() == task_cmdline(task_id):
                return int(pid)
        time.sleep(wait)
    return None


#################
# Konro helpers #
#################

def konro_add(pid: int, task_id: str, node_name: str, task: Dict[str, Any]) -> None:
    """Register the task process in Konro (POST /add)."""
    payload = {"pid": pid,
               "name": task_id,
               "type": "CONTAINER",
               # extra fields for the security-aware policy (ignored by the current Konro)
               "node": node_name,
               "sensitive": task["sensitive"],
               "sources": task["env"]["SOURCES"].split(",")}
    req = requests.post(f"{KONRO_ADDR}/add", data=json.dumps(payload))
    req.raise_for_status()


##################
# Task lifecycle #
##################

def find_task(server: Server, project: Project, docker_client, task_id: str) -> Optional[Item]:
    """Return the worker node where the task is running (None if not running)."""
    for node in get_nodes_id_by_name_regexp(server, project, WORKERS_PATTERN):
        container = docker_client.containers.get(get_node_docker_container_id(server, project, node.id))
        if container.status == "running" and get_task_host_pid(container, task_id, attempts=1):
            return node
    return None


def launch_task(server: Server, project: Project, docker_client, task_id: str, node_name: Optional[str] = None) -> int:
    """Copy the application into the worker, start the task and register it in Konro."""
    task = TASKS[task_id]
    node_name = node_name or task["node"]
    container = get_node_container(server, project, docker_client, node_name)

    copy_app_to_container(container, APP_PATH, APP_DIR_IN_WORKER)
    env = {k: str(v) for k, v in {**COMMON_ENV, **task["env"]}.items()}
    container.exec_run(task_cmdline(task_id), environment=env, detach=True)

    pid = get_task_host_pid(container, task_id)
    if pid is None:
        raise RuntimeError(f"{task_id} did not start on {node_name}")
    print(f"Starting {task_id} on {node_name}... OK (pid {pid})")

    try:
        konro_add(pid, task_id, node_name, task)
        print(f"Registering {task_id} in Konro... OK")
    except requests.exceptions.RequestException as e:
        print(f"Registering {task_id} in Konro... ERROR ({e})")
    return pid


def kill_task(server: Server, project: Project, docker_client, task_id: str) -> Optional[str]:
    """Stop the task wherever it is running. Returns the node where it was running."""
    node = find_task(server, project, docker_client, task_id)
    if node is None:
        print(f"{task_id} is not running")
        return None
    container = docker_client.containers.get(get_node_docker_container_id(server, project, node.id))
    container.exec_run(["pkill", "-f", f"{APP_PATH.name} {task_id}$"])
    print(f"Stopping {task_id} on {node.name}... OK")
    return node.name


def migrate_task(server: Server, project: Project, docker_client, task_id: str, dest_node: str) -> int:
    """Kill & restart: stop the task where it runs and start it on dest_node."""
    src = kill_task(server, project, docker_client, task_id)
    print(f"Migrating {task_id}: {src} -> {dest_node}")
    return launch_task(server, project, docker_client, task_id, dest_node)


def print_status(server: Server, project: Project, docker_client) -> None:
    """Print where each task is running."""
    for task_id, task in TASKS.items():
        node = find_task(server, project, docker_client, task_id)
        where = node.name if node else "not running"
        print(f"{task_id:4} sensitive={str(task['sensitive']):5} -> {where}")


if __name__ == "__main__":
    check_local_gns3_config()
    server = Server(*read_local_gns3_config())
    project = get_project_by_name(server, PROJECT_NAME)
    if not project:
        sys.exit(f"Project {PROJECT_NAME} does not exist!")

    docker_client = docker.from_env()
    docker_client.ping()

    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    args = sys.argv[2:]

    if cmd == "launch-all":
        for task_id in TASKS:
            launch_task(server, project, docker_client, task_id)
    elif cmd == "launch" and args:
        launch_task(server, project, docker_client, args[0], args[1] if len(args) > 1 else None)
    elif cmd == "kill" and args:
        kill_task(server, project, docker_client, args[0])
    elif cmd == "migrate" and len(args) == 2:
        migrate_task(server, project, docker_client, args[0], args[1])
    elif cmd == "status":
        print_status(server, project, docker_client)
    else:
        sys.exit(__doc__)