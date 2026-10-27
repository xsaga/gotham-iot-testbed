import re, json, subprocess, requests, random
from gns3utils import *
import sys

KONRO = "http://localhost:8080"
REQ_NAME = "security"
s = Server(*read_local_gns3_config())
p = get_project_by_name(s, "konro_scenario")
regex = sys.argv[1]

all_nodes = get_nodes_id_by_name_regexp(s,p, re.compile(regex))
if(all_nodes):
    ## pick random infected node
    for n in all_nodes:
        if(random.choice([0, 1]) == 0):
            cid = get_node_docker_container_id(s, p, n.id)
            pid = subprocess.run(["docker", "inspect", "-f", "{{.State.Pid}}", cid],
                                    capture_output=True, text=True).stdout.strip()
            
            if not pid or pid == "0":
                    print(f"{n.name}: non in esecuzione, saltato")
                    continue
            
            r = requests.post(f"{KONRO}/{REQ_NAME}",
                                data=json.dumps({"pid": int(pid), "name": n.name, "type": "CONTAINER"}),
                                headers={"Content-Type": "application/json"})
            print(f"{n.name}: pid {pid} -> {r.status_code}")
else:
     print(f"No nodes matching with regex {regex}")