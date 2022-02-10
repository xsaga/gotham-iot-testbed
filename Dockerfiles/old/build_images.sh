#!/usr/bin/env bash
set -e

docker build --file ./mqtt_cloud/Dockerfile --tag mqtt-cloud ./mqtt_cloud
docker build --file ./coap_cloud/Dockerfile --tag coap-cloud ./coap_cloud
docker build --file ./debug_client/Dockerfile --tag debug-client ./debug_client

docker build --file ./mqtt_client_t1/Dockerfile --tag mqtt-device-t1 ./mqtt_client_t1
docker build --file ./mqtt_client_t2/Dockerfile --tag mqtt-device-t2 ./mqtt_client_t2
docker build --file ./coap_client_t1/Dockerfile --tag coap-device-t1 ./coap_client_t1

docker build --no-cache --file ./command_control/Dockerfile --tag command-control-server ./command_control
docker build --no-cache --file ./compromised/Dockerfile.mqtt_client_t1 --tag mqtt-device-t1-compromised ./compromised
docker build --no-cache --file ./compromised/Dockerfile.mqtt_client_t2 --tag mqtt-device-t2-compromised ./compromised
docker build --no-cache --file ./compromised/Dockerfile.coap_client_t1 --tag coap-device-t1-compromised ./compromised
