# iot-sim

Work in Progres...

Tested on Ubuntu 20.04.4 LTS and 22.04 LTS

## Dependencies

- make

- Python 3

- Docker: https://docs.docker.com/engine/install/

- GNS3: https://www.gns3.com/

## Python virtual environment

```
$ python3 -m venv venv
(venv) $ pip install -r requirements.txt
```

## Create router template

Run: `make vyosiso`

The artifacts will be downloaded into the ~/Downloads directory. Follow the instructions to import appliances in GNS3 https://docs.gns3.com/docs/using-gns3/beginners/import-gns3-appliance/. The router appliance file is located at `router/iotsim-vyos.gns3a`.

## Create Docker images

Run: `make`

## Template creation

GNS3 must be running.
Inside the `src/` directory run:
```
(venv) $ python3 create_templates.py
```

## Topology builder

GNS3 must be running.
Inside the `src/` directory run:
```
(venv) $ python3 create_topology_iotsim.py
```

## Scenario generator

GNS3 must be running.
Inside the `src/` directory run:
```
(venv) $ python3 run_scenario_iotsim.py
```
