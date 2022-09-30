"""Convert Makefile to Graphviz"""

from pathlib import Path
from typing import Dict

from parseutils import parse_project_makefile

import graphviz


def name_filterer(s: str) -> str:
    if s.startswith("buildstatus/"):
        return s.replace("buildstatus/","")

    if s.startswith("Dockerfiles/"):
        return s.replace("Dockerfiles/", "")

    return s


def node_name_attributes(s: str) -> Dict:
    # is a Docker container target
    if s.startswith("buildstatus/"):
        return {"style":"filled", "shape": "box", "color": "#ff0000", "fillcolor": "pink", "fontname": "Arial"}

    # router target
    if s.startswith("vyosiso"):
        return {"style":"filled", "shape": "box", "color": "#ff0000", "fillcolor": "pink", "fontname": "Arial"}

    # config file
    if s.startswith("$("):
        return {"style":"filled", "shape": "ellipse", "color": "#00ff00", "fillcolor": "lightgreen", "fontname": "Arial"}

    p = Path("../") / s
    # is a file
    if p.is_file():
        return {"style":"filled", "shape":"ellipse", "color": "#0000ff", "fillcolor": "lightcyan", "fontname": "Arial"}

    # not a file, but template exists
    if (not p.is_file()) and p.with_name(p.name+".template").is_file():
        return {"style":"filled", "shape":"ellipse", "color": "yellow", "fillcolor": "lightyellow", "fontname": "Arial"}

    # is a file glob
    if p.parent.is_dir() and ("*" in p.name):
        return {"style":"filled", "shape":"ellipse", "color": "#0000ff", "fillcolor": "lightcyan", "fontname": "Arial"}
    return {}


makefile_path = Path("../Makefile")
make_rules = parse_project_makefile(makefile_path)

ignore_targets = [".PHONY", "all", "templates", "clean", "imagerm", "Mirai_experimentation"]

all_nodes = []
for rule in make_rules:
    all_nodes.extend(rule["targets"])
    all_nodes.extend(rule["prerequisites"])
all_nodes = set(all_nodes)


graph = graphviz.Digraph()  # (graph_attr={"ratio":"fill", "size":"8.3,11.7"})

for node in all_nodes:
    if node in ignore_targets:
        continue
    graph.node(name_filterer(node), **node_name_attributes(node))

for rule in make_rules:
    to_node = rule["targets"][0]
    if to_node in ignore_targets:
        continue
    for from_node in rule["prerequisites"]:
        if from_node in ignore_targets:
            continue
        graph.edge(name_filterer(from_node), name_filterer(to_node))

print(graph.source)
# sfdp -Nfontsize="10" -Gfontsize="10" -Gratio="0.707" -Nwidth=0 -Nheight=0 -Nmargin=0 -Goverlap=prism -Tpdf graph.gv -o graph.pdf
# graph.render("/mnt/c/Users/xsaezdecamara/Desktop/ttt", format="pdf", engine="fdp")
