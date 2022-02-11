BUILD_CMD = echo docker build
ifdef NOCACHE
BUILD_CMD += --no-cache
endif

.PHONY: all clean imagerm Mirai_experimentation

all: buildstatus/DNS buildstatus/certificates \
     buildstatus/Merlin buildstatus/Mirai_builder buildstatus/Mirai_cnc buildstatus/Mirai_bot \
     buildstatus/mqtt_broker_1.6 buildstatus/mqtt_broker_tls \
     buildstatus/mqtt_client_t1 buildstatus/mqtt_client_t2 \
     buildstatus/coap_server buildstatus/coap_cloud \
     buildstatus/mqtt_client_t1_compromised buildstatus/mqtt_client_t2_compromised buildstatus/coap_server_compromised \
     buildstatus/debug_client


Mirai_experimentation: Dockerfiles/malware/Mirai/Dockerfile_experimentation
	$(BUILD_CMD) --file $< --tag iotsim/mirai-experimentation Dockerfiles/malware/Mirai

buildstatus/DNS: Dockerfiles/DNS/Dockerfile Dockerfiles/DNS/dnsmasq.conf
	$(BUILD_CMD) --file $< --tag iotsim/dns Dockerfiles/DNS
	sleep 2
	@touch $@

buildstatus/certificates: Dockerfiles/certificates/Dockerfile
	$(BUILD_CMD) --file $< --tag iotsim/certificates Dockerfiles/certificates
	sleep 2
	@touch $@

buildstatus/Merlin: Dockerfiles/malware/Merlin/Dockerfile
	$(BUILD_CMD) --file $< --tag iotsim/merlin-cnc Dockerfiles/malware/Merlin
	sleep 2
	@touch $@

buildstatus/Mirai_builder: Dockerfiles/malware/Mirai/Dockerfile_builder
	$(BUILD_CMD) --file $< --tag iotsim/mirai-builder Dockerfiles/malware/Mirai
	sleep 2
	@touch $@

buildstatus/Mirai_cnc: Dockerfiles/malware/Mirai/Dockerfile_cnc buildstatus/Mirai_builder
	$(BUILD_CMD) --file $< --tag iotsim/mirai-cnc Dockerfiles/malware/Mirai
	sleep 2
	@touch $@

buildstatus/Mirai_bot: Dockerfiles/malware/Mirai/Dockerfile_bot buildstatus/Mirai_builder
	$(BUILD_CMD) --file $< --tag iotsim/mirai-bot Dockerfiles/malware/Mirai
	sleep 2
	@touch $@

buildstatus/mqtt_broker_1.6: Dockerfiles/iot/mqtt_broker/Dockerfile_1.6
	$(BUILD_CMD) --file $< --tag iotsim/mqtt-broker-1.6 Dockerfiles/iot/mqtt_broker
	sleep 2
	@touch $@

buildstatus/mqtt_broker_tls: Dockerfiles/iot/mqtt_broker/Dockerfile_tls Dockerfiles/iot/mqtt_broker/mosquitto_tls.conf buildstatus/certificates
	$(BUILD_CMD) --file $< --tag iotsim/mqtt-broker-tls Dockerfiles/iot/mqtt_broker
	sleep 2
	@touch $@

buildstatus/mqtt_client_t1: Dockerfiles/iot/mqtt_client_t1/Dockerfile Dockerfiles/iot/mqtt_client_t1/client.py
	$(BUILD_CMD) --file $< --tag iotsim/mqtt-client-t1 Dockerfiles/iot/mqtt_client_t1
	sleep 2
	@touch $@

buildstatus/mqtt_client_t2: Dockerfiles/iot/mqtt_client_t2/Dockerfile Dockerfiles/iot/mqtt_client_t2/client.py
	$(BUILD_CMD) --file $< --tag iotsim/mqtt-client-t2 Dockerfiles/iot/mqtt_client_t2
	sleep 2
	@touch $@

buildstatus/coap_server: Dockerfiles/iot/coap_server/Dockerfile Dockerfiles/iot/coap_server/coap-server-mod.c
	$(BUILD_CMD) --file $< --tag iotsim/coap-server Dockerfiles/iot/coap_server
	sleep 2
	@touch $@

buildstatus/coap_cloud: Dockerfiles/iot/coap_cloud/Dockerfile Dockerfiles/iot/coap_cloud/coap-client-mod.c Dockerfiles/iot/coap_cloud/coap_cloud.py
	$(BUILD_CMD) --file $< --tag iotsim/coap-cloud Dockerfiles/iot/coap_cloud
	sleep 2
	@touch $@

buildstatus/debug_client: Dockerfiles/iot/debug_client/Dockerfile
	$(BUILD_CMD) --file $< --tag iotsim/debug-client Dockerfiles/iot/debug_client
	sleep 2
	@touch $@

buildstatus/mqtt_client_t1_compromised: Dockerfiles/iot/compromised/Dockerfile.mqtt_client_t1 buildstatus/Merlin buildstatus/mqtt_client_t1
	$(BUILD_CMD) --file $< --tag iotsim/mqtt-client-compromised-t1 Dockerfiles/iot/compromised
	sleep 2
	@touch $@

buildstatus/mqtt_client_t2_compromised: Dockerfiles/iot/compromised/Dockerfile.mqtt_client_t2 buildstatus/Merlin buildstatus/mqtt_client_t2
	$(BUILD_CMD) --file $< --tag iotsim/mqtt-client-compromised-t2 Dockerfiles/iot/compromised
	sleep 2
	@touch $@

buildstatus/coap_server_compromised: Dockerfiles/iot/compromised/Dockerfile.coap_client_t1 buildstatus/Merlin buildstatus/coap_server
	$(BUILD_CMD) --file $< --tag iotsim/coap-server-compromised Dockerfiles/iot/compromised
	sleep 2
	@touch $@

clean:
	rm -f buildstatus/*

imagerm: clean
	docker image ls | grep "^iotsim/" | awk '{print $$3}' | xargs docker image rm -f

