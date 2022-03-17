import json
import re
import requests
import string
import time
import warnings

from pathlib import Path

from parseutils import get_variable_from_file, parse_project_makefile
from gns3utils import Server, check_server_version, create_docker_template, get_all_templates, read_local_gns3_config


YELLOW = "\033[93m"
GREEN = "\033[92m"
BLUE = "\033[94m"
RESET = "\033[0m"


def clean_name(name: str) -> str:
    """Replace non ascii or digits with '-'."""
    allow = string.ascii_letters + string.digits + "."
    return "".join([c if c in allow else "-" for c in name])


def get_make_rule_by_target_name(rules: list, target: str):
    return next(filter(lambda t: target in t["targets"], rules))


def dict_to_env_str(env: dict):
    res = []
    for k, v in env.items():
        res.append(f"{k}={v}")
    return "\n".join(res)


server = Server(*read_local_gns3_config())
check_server_version(server)

init_templates = get_all_templates(server)
print(f"{len(init_templates)} templates found in the GNS3 server.")

makefile_path = Path("../Makefile")
print(f"Parsing project makefile at {makefile_path.resolve()}")
make_rules = parse_project_makefile(makefile_path)
print(f"{len(make_rules)} rules found")

all_docker_targets = get_make_rule_by_target_name(make_rules, "all")["prerequisites"]
print(f"{len(all_docker_targets)} docker targets found")


all_project_py_files = list(Path("../Dockerfiles").rglob("*.py"))
all_scanned_py_files = []


for target in all_docker_targets:
    target_rule = get_make_rule_by_target_name(make_rules, target)
    depends = target_rule["prerequisites"]
    depends_py = list(filter(lambda d: d.endswith(".py"), depends))

    print(f"{YELLOW}[*] {target} depends on:{RESET}")
    for dep in depends:
        print(f"\t{dep}")

    # parse python file dependencies to search for the 'config' variable
    # to build the template environment variables.
    env_vars = ""
    if depends_py:
        print(f"\t{YELLOW}Parsing python dependencies for the `config' variable{RESET}")
        for pydep in depends_py:
            print(f"\t\tParsing {pydep}", end="", flush=True)
            try:
                pydep_file = Path("..") / pydep
                all_scanned_py_files.append(pydep_file)
                config = get_variable_from_file(pydep_file, "config")
                print("... found.")
                print(f"\t\t\t{GREEN}{config}{RESET}")
                env_vars = dict_to_env_str(config)
                break
            except ValueError:
                print("... not found.")

    # parse target recipes to find the docker image tag
    print(f"\t{YELLOW}Parsing {target} recipes{RESET}")
    docker_tag = ""
    for recipe in target_rule["recipes"]:
        print(f"\t\t{recipe}")
        match = re.search(r"--tag\s+([^ ]+)", recipe)
        if match:
            docker_tag = match.group(1)
            print(f"\t\t\tDocker tag found {GREEN}{docker_tag}{RESET}")
            break

    if not docker_tag:
        raise RuntimeError(f"No docker tag found for the docker target {target}.")

    # create the GNS3 template
    if ":" in docker_tag:
        docker_image = docker_tag
    else:
        docker_image = docker_tag + ":latest"

    template_name = clean_name(docker_tag)
    print(f"\t{YELLOW}Creating docker GNS3 template:{RESET}\n\tName  = {template_name}\n\tImage = {docker_image}\n\tEnv   = {env_vars.encode('unicode_escape').decode('utf-8')}")
    created_template = create_docker_template(server, template_name, docker_image, env_vars)
    print(f"\tCreated template id {BLUE}{created_template['template_id']}{RESET}")
    print("\n")
    time.sleep(1)

# checks
diff_py_files = set(all_project_py_files).symmetric_difference(all_scanned_py_files)
if diff_py_files:
    warnings.warn(f"The python files in the Dockerfiles directory do not match all the python files declared in the Makefile. Is this OK?: {diff_py_files}", RuntimeWarning)

# TODO check that vyos templates exists. else warn for manual installation
openvswitch_appliance_path = Path("../switch/openvswitch.gns3a")
with open(openvswitch_appliance_path, "r", encoding="utf-8") as f:
    openvswitch_appliance = json.load(f)

openvswitch_template_payload = {'adapters': openvswitch_appliance["docker"]['adapters'],
                                'category': 'switch',
                                'compute_id': 'local',
                                'image': openvswitch_appliance["docker"]["image"],
                                'name': openvswitch_appliance["name"],
                                'symbol': ':/symbols/multilayer_switch.svg',
                                'template_type': 'docker',
                                'usage': openvswitch_appliance["usage"]}
req = requests.post(f"http://{server.addr}:{server.port}/v2/templates", data=json.dumps(openvswitch_template_payload), auth=(server.user, server.password))
req.raise_for_status()
openvswitch_template = req.json()
print(f"{BLUE}{openvswitch_template}{RESET}")
