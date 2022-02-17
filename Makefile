BUILD_CMD = echo docker build
ifdef NOCACHE
BUILD_CMD += --no-cache
endif

CONFIG_FILE = iot-sim.config
include $(CONFIG_FILE)


.PHONY: all templates clean imagerm Mirai_experimentation

all: buildstatus/DNS buildstatus/certificates \
     buildstatus/Merlin buildstatus/Mirai_builder buildstatus/Mirai_cnc buildstatus/Mirai_bot \
     buildstatus/mqtt_broker_1.6 buildstatus/mqtt_broker_tls \
     buildstatus/mqtt_client_t1 buildstatus/mqtt_client_t2 \
     buildstatus/coap_server buildstatus/coap_cloud \
     buildstatus/ip_camera_street buildstatus/ip_camera_museum buildstatus/stream_server buildstatus/stream_consumer \
     buildstatus/mqtt_client_t1_compromised buildstatus/mqtt_client_t2_compromised buildstatus/coap_server_compromised \
     buildstatus/debug_client

templates: Dockerfiles/certificates/Dockerfile Dockerfiles/DNS/dnsmasq.conf \
           Dockerfiles/malware/Mirai/Dockerfile.cnc Dockerfiles/malware/Mirai/Dockerfile.builder

Dockerfiles/certificates/Dockerfile: Dockerfiles/certificates/Dockerfile.template $(CONFIG_FILE)
	sed 's/!PLACEHOLDER-MQTT_TLS_BROKER_CN!/$(MQTT_TLS_BROKER_CN)/g' $< > $@

Dockerfiles/DNS/dnsmasq.conf: Dockerfiles/DNS/dnsmasq.conf.template $(CONFIG_FILE)
	sed -e 's/!PLACEHOLDER-LOCAL_DOMAIN!/$(LOCAL_DOMAIN)/g' \
            -e 's/!PLACEHOLDER-MIRAI_CNC_IPADDR!/$(MIRAI_CNC_IPADDR)/g' \
            -e 's/!PLACEHOLDER-MIRAI_REPORT_IPADDR!/$(MIRAI_REPORT_IPADDR)/g' $< > $@

Dockerfiles/malware/Mirai/Dockerfile.cnc: Dockerfiles/malware/Mirai/Dockerfile.cnc.template $(CONFIG_FILE)
	sed -e 's/!PLACEHOLDER-MIRAI_DB_USERNAME!/$(MIRAI_DB_USERNAME)/g' \
            -e 's/!PLACEHOLDER-MIRAI_DB_PASSWORD!/$(MIRAI_DB_PASSWORD)/g' $< > $@

Dockerfiles/malware/Mirai/Dockerfile.builder: Dockerfiles/malware/Mirai/Dockerfile.builder.template $(CONFIG_FILE)
	LAB_DNS_IPADDR_COMMAS=$(shell echo $(LAB_DNS_IPADDR) | tr "." ","); \
	sed "s/!PLACEHOLDER-LAB_DNS_IPADDR!/$$LAB_DNS_IPADDR_COMMAS/g" $< > $@

Mirai_experimentation: Dockerfiles/malware/Mirai/Dockerfile.experimentation
	$(BUILD_CMD) --file $< --tag iotsim/mirai-experimentation Dockerfiles/malware/Mirai

buildstatus/DNS: Dockerfiles/DNS/Dockerfile Dockerfiles/DNS/dnsmasq.conf
	$(BUILD_CMD) --file $< --tag iotsim/dns Dockerfiles/DNS
	@touch $@

buildstatus/certificates: Dockerfiles/certificates/Dockerfile
	$(BUILD_CMD) --file $< --tag iotsim/certificates Dockerfiles/certificates
	@touch $@

buildstatus/Merlin: Dockerfiles/malware/Merlin/Dockerfile $(CONFIG_FILE)
	$(BUILD_CMD) --build-arg MERLIN_RELEASE_VER=$(MERLIN_RELEASE_VER) --file $< --tag iotsim/merlin-cnc Dockerfiles/malware/Merlin
	@touch $@

buildstatus/Mirai_builder: Dockerfiles/malware/Mirai/Dockerfile.builder
	$(BUILD_CMD) --file $< --tag iotsim/mirai-builder Dockerfiles/malware/Mirai
	@touch $@

buildstatus/Mirai_cnc: Dockerfiles/malware/Mirai/Dockerfile.cnc buildstatus/Mirai_builder
	$(BUILD_CMD) --file $< --tag iotsim/mirai-cnc Dockerfiles/malware/Mirai
	@touch $@

buildstatus/Mirai_bot: Dockerfiles/malware/Mirai/Dockerfile.bot buildstatus/Mirai_builder
	$(BUILD_CMD) --file $< --tag iotsim/mirai-bot Dockerfiles/malware/Mirai
	@touch $@

buildstatus/mqtt_broker_1.6: Dockerfiles/iot/mqtt_broker/Dockerfile.1.6
	$(BUILD_CMD) --file $< --tag iotsim/mqtt-broker-1.6 Dockerfiles/iot/mqtt_broker
	@touch $@

buildstatus/mqtt_broker_tls: Dockerfiles/iot/mqtt_broker/Dockerfile.tls Dockerfiles/iot/mqtt_broker/mosquitto_tls.conf buildstatus/certificates
	$(BUILD_CMD) --file $< --tag iotsim/mqtt-broker-tls Dockerfiles/iot/mqtt_broker
	@touch $@

buildstatus/mqtt_client_t1: Dockerfiles/iot/mqtt_client_t1/Dockerfile Dockerfiles/iot/mqtt_client_t1/client.py
	$(BUILD_CMD) --file $< --tag iotsim/mqtt-client-t1 Dockerfiles/iot/mqtt_client_t1
	@touch $@

buildstatus/mqtt_client_t2: Dockerfiles/iot/mqtt_client_t2/Dockerfile Dockerfiles/iot/mqtt_client_t2/client.py
	$(BUILD_CMD) --file $< --tag iotsim/mqtt-client-t2 Dockerfiles/iot/mqtt_client_t2
	@touch $@

buildstatus/coap_server: Dockerfiles/iot/coap_server/Dockerfile Dockerfiles/iot/coap_server/coap-server-mod.c
	$(BUILD_CMD) --file $< --tag iotsim/coap-server Dockerfiles/iot/coap_server
	@touch $@

buildstatus/coap_cloud: Dockerfiles/iot/coap_cloud/Dockerfile Dockerfiles/iot/coap_cloud/coap-client-mod.c Dockerfiles/iot/coap_cloud/coap_cloud.py
	$(BUILD_CMD) --file $< --tag iotsim/coap-cloud Dockerfiles/iot/coap_cloud
	@touch $@

buildstatus/ip_camera_street: Dockerfiles/iot/ip_camera/Dockerfile.720_15fps_noaudio Dockerfiles/iot/ip_camera/street_london_rainy_night.mp4
	$(BUILD_CMD) --file $< --tag iotsim/ip-camera-street Dockerfiles/iot/ip_camera
	@touch $@

buildstatus/ip_camera_museum: Dockerfiles/iot/ip_camera/Dockerfile.720_grayscale_25fps_noaudio Dockerfiles/iot/ip_camera/museum_lebanon.mp4
	$(BUILD_CMD) --file $< --tag iotsim/ip-camera-museum Dockerfiles/iot/ip_camera
	@touch $@

buildstatus/stream_server: Dockerfiles/iot/stream_server/Dockerfile Dockerfiles/iot/stream_server/rtsp-simple-server.yml
	$(BUILD_CMD) --file $< --tag iotsim/stream-server Dockerfiles/iot/stream_server
	@touch $@

buildstatus/stream_consumer: Dockerfiles/iot/stream_consumer/Dockerfile
	$(BUILD_CMD) --file $< --tag iotsim/stream-consumer Dockerfiles/iot/stream_consumer
	@touch $@

buildstatus/debug_client: Dockerfiles/iot/debug_client/Dockerfile
	$(BUILD_CMD) --file $< --tag iotsim/debug-client Dockerfiles/iot/debug_client
	@touch $@

buildstatus/mqtt_client_t1_compromised: Dockerfiles/iot/compromised/Dockerfile.mqtt_client_t1 buildstatus/Merlin buildstatus/mqtt_client_t1
	$(BUILD_CMD) --file $< --tag iotsim/mqtt-client-compromised-t1 Dockerfiles/iot/compromised
	@touch $@

buildstatus/mqtt_client_t2_compromised: Dockerfiles/iot/compromised/Dockerfile.mqtt_client_t2 buildstatus/Merlin buildstatus/mqtt_client_t2
	$(BUILD_CMD) --file $< --tag iotsim/mqtt-client-compromised-t2 Dockerfiles/iot/compromised
	@touch $@

buildstatus/coap_server_compromised: Dockerfiles/iot/compromised/Dockerfile.coap_client_t1 buildstatus/Merlin buildstatus/coap_server
	$(BUILD_CMD) --file $< --tag iotsim/coap-server-compromised Dockerfiles/iot/compromised
	@touch $@

clean:
	rm -f buildstatus/*
	rm -f Dockerfiles/certificates/Dockerfile
	rm -f Dockerfiles/DNS/dnsmasq.conf
	rm -f Dockerfiles/malware/Mirai/Dockerfile.cnc
	rm -f Dockerfiles/malware/Mirai/Dockerfile.builder

imagerm: clean
	docker image ls | grep "^iotsim/" | awk '{print $$3}' | xargs docker image rm -f

