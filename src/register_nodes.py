import re, json, subprocess, requests
from gns3utils import *

KONRO = "http://localhost:8080"
s = Server(*read_local_gns3_config())
p = get_project_by_name(s, "gotham_scenario")

for n in get_nodes_id_by_name_regexp(s, p, re.compile("iotsim-.*")):
    cid = get_node_docker_container_id(s, p, n.id)
    pid = subprocess.run(["docker", "inspect", "-f", "{{.State.Pid}}", cid],
                         capture_output=True, text=True).stdout.strip()
    if not pid or pid == "0":
        print(f"{n.name}: non in esecuzione, saltato")
        continue
    r = requests.post(f"{KONRO}/add",
                      data=json.dumps({"pid": int(pid), "name": n.name, "type": "CONTAINER"}),
                      headers={"Content-Type": "application/json"})
    print(f"{n.name}: pid {pid} -> {r.status_code}")
