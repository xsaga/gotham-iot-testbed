import json, re, graphviz

dot = graphviz.Graph()

with open("iot_sim.gns3", "r") as f:
    project = json.load(f)

topology = project["topology"]
nodes = topology["nodes"]

map_image_color = {"iotsim/dns": "#4d4d4d",
                   "iotsim/ntp": "#999999",
                   "iotsim/merlin-cnc": "#984ea3",
                   "iotsim/mirai-cnc": "#800026",
                   "iotsim/mirai-bot": "#ff0000",
                   "iotsim/mirai-scan-listener": "#bd0026",
                   "iotsim/mirai-loader": "#e31a1c",
                   "iotsim/mirai-wget-loader": "#fc4e2a",
                   "iotsim/scanner": "#ae017e",
                   "iotsim/amplification-coap": "#dd3497",
                   "iotsim/mqtt-attacks": "#f768a1",
                   "iotsim/metasploit": "#fa9fb5",
                   "iotsim/mqtt-broker-1.6": "#ffe901",
                   "iotsim/mqtt-broker-1.6-auth": "#fcb700",
                   "iotsim/mqtt-broker-tls": "#fc8e01",
                   "iotsim/air-quality": "#005a32",
                   "iotsim/cooler-motor": "#fc8d62",
                   "iotsim/predictive-maintenance": "#66c2a5",
                   "iotsim/hydraulic-system": "#8da0cb",
                   "iotsim/building-monitor": "#0868ac",
                   "iotsim/domotic-monitor": "#084081",
                   "iotsim/city-power": "#ffffd4",
                   "iotsim/city-power-tls": "#fee391",
                   "iotsim/city-power-cloud": "#fec44f",
                   "iotsim/combined-cycle": "#fee5d9",
                   "iotsim/combined-cycle-tls": "#fcaea1",
                   "iotsim/combined-cycle-cloud": "#fb6a4a",
                   "iotsim/ip-camera-street": "#a8ddb5",
                   "iotsim/ip-camera-museum": "#ccebc5",
                   "iotsim/stream-server": "#e0f3db",
                   "iotsim/stream-consumer": "#f7fcf0",
                   "iotsim/debug-client": "#7fff00"}

for node in nodes:
    node_id = node["node_id"].replace("-", "")
    if node["name"].startswith("OpenvS"):
        attrs={"label": "S",
               "shape": "circle",
               "fixedsize": "true",
               "style": "filled",
               "fillcolor": "#f5f5f5",
               "width": "0.3"}
    elif node["name"].startswith("VyOS"):
        attrs={"label": "R",
               "shape": "circle",
               "fixedsize": "true",
               "style": "filled",
               "fillcolor": "#bebebe",
               "width": "0.4"}
    else:
        attrs={"shape": "point",
               "width": "0.2",
               "fillcolor": map_image_color.get(node["properties"]["image"].split(":")[0], "#7fff00")}

    dot.node(node_id, **attrs)

for link in topology["links"]:
    n1 = link["nodes"][0]["node_id"].replace("-", "")
    n2 = link["nodes"][1]["node_id"].replace("-", "")
    dot.edge(n1, n2)

print(dot.source)


dot.render("graph", format="pdf", engine="twopi")  # twopi, neato
