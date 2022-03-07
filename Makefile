BUILD_CMD = docker build
ifdef NOCACHE
BUILD_CMD += --no-cache
endif

CONFIG_FILE = iot-sim.config
include $(CONFIG_FILE)


.PHONY: all templates vyosiso clean imagerm Mirai_experimentation

all: buildstatus/DNS buildstatus/certificates buildstatus/NTP \
     buildstatus/Merlin buildstatus/Mirai_builder buildstatus/Mirai_cnc buildstatus/Mirai_bot buildstatus/Mirai_scan_listener buildstatus/Mirai_loader buildstatus/Mirai_wget_loader \
     buildstatus/mqtt_broker_1.6 buildstatus/mqtt_broker_tls \
     buildstatus/mqtt_client_t1 buildstatus/mqtt_client_t2 \
     buildstatus/air_quality buildstatus/cooler_motor buildstatus/predictive_maintenance \
     buildstatus/hydraulic_system buildstatus/building_monitor buildstatus/domotic_monitor \
     buildstatus/coap_server buildstatus/coap_cloud buildstatus/city_power buildstatus/city_power_tls \
     buildstatus/combined_cycle buildstatus/combined_cycle_tls \
     buildstatus/city_power_cloud buildstatus/combined_cycle_cloud \
     buildstatus/ip_camera_street buildstatus/ip_camera_museum buildstatus/stream_server buildstatus/stream_consumer \
     buildstatus/mqtt_client_t1_compromised buildstatus/mqtt_client_t2_compromised buildstatus/coap_server_compromised \
     buildstatus/debug_client

templates: Dockerfiles/certificates/Dockerfile Dockerfiles/DNS/dnsmasq.conf \
           Dockerfiles/malware/Mirai/Dockerfile.cnc Dockerfiles/malware/Mirai/Dockerfile.builder

vyosiso:
	wget https://s3.amazonaws.com/s3-us.vyos.io/snapshot/vyos-1.3.0-rc6/vyos-1.3.0-rc6-amd64.iso

Dockerfiles/certificates/Dockerfile: Dockerfiles/certificates/Dockerfile.template $(CONFIG_FILE)
	sed 's/!PLACEHOLDER-MQTT_TLS_BROKER_CN!/$(MQTT_TLS_BROKER_CN)/g' $< > $@

Dockerfiles/DNS/dnsmasq.conf: Dockerfiles/DNS/dnsmasq.conf.template $(CONFIG_FILE)
	sed -e 's/!PLACEHOLDER-LOCAL_DOMAIN!/$(LOCAL_DOMAIN)/g' \
            -e 's/!PLACEHOLDER-MIRAI_CNC_IPADDR!/$(MIRAI_CNC_IPADDR)/g' \
            -e 's/!PLACEHOLDER-MIRAI_REPORT_IPADDR!/$(MIRAI_REPORT_IPADDR)/g' $< > $@

Dockerfiles/malware/Mirai/Dockerfile.cnc: Dockerfiles/malware/Mirai/Dockerfile.cnc.template $(CONFIG_FILE)
	sed -e 's/!PLACEHOLDER-MIRAI_DB_USERNAME!/$(MIRAI_DB_USERNAME)/g' \
            -e 's/!PLACEHOLDER-MIRAI_DB_PASSWORD!/$(MIRAI_DB_PASSWORD)/g' $< > $@

Dockerfiles/malware/Mirai/Dockerfile.builder: Dockerfiles/malware/Mirai/Dockerfile.builder.template Dockerfiles/malware/Mirai/get_random_ip.patch $(CONFIG_FILE)
	LAB_DNS_IPADDR_COMMAS=$(shell echo $(LAB_DNS_IPADDR) | tr "." ","); \
	sed -e "s/!PLACEHOLDER-LAB_DNS_IPADDR!/$$LAB_DNS_IPADDR_COMMAS/g" \
	    -e 's/!PLACEHOLDER-MIRAI_WGET_LOADER_IPADDR!/$(MIRAI_WGET_LOADER_IPADDR)/g' $< > $@

Mirai_experimentation: Dockerfiles/malware/Mirai/Dockerfile.experimentation
	$(BUILD_CMD) --file $< --tag iotsim/mirai-experimentation Dockerfiles/malware/Mirai

buildstatus/DNS: Dockerfiles/DNS/Dockerfile Dockerfiles/DNS/dnsmasq.conf
	$(BUILD_CMD) --file $< --tag iotsim/dns Dockerfiles/DNS
	@touch $@

buildstatus/certificates: Dockerfiles/certificates/Dockerfile
	$(BUILD_CMD) --file $< --tag iotsim/certificates Dockerfiles/certificates
	@touch $@

buildstatus/NTP: Dockerfiles/NTP/Dockerfile Dockerfiles/NTP/chrony.conf
	$(BUILD_CMD) --file $< --tag iotsim/ntp Dockerfiles/NTP
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

buildstatus/Mirai_scan_listener: Dockerfiles/malware/Mirai/Dockerfile.scanlistener buildstatus/Mirai_builder
	$(BUILD_CMD) --file $< --tag iotsim/mirai-scan-listener Dockerfiles/malware/Mirai
	@touch $@

buildstatus/Mirai_loader: Dockerfiles/malware/Mirai/Dockerfile.loader buildstatus/Mirai_builder
	$(BUILD_CMD) --file $< --tag iotsim/mirai-loader Dockerfiles/malware/Mirai
	@touch $@

buildstatus/Mirai_wget_loader: Dockerfiles/malware/Mirai/Dockerfile.wget_loader buildstatus/Mirai_builder
	$(BUILD_CMD) --file $< --tag iotsim/mirai-wget-loader Dockerfiles/malware/Mirai
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

buildstatus/air_quality: Dockerfiles/iot/air_quality/Dockerfile Dockerfiles/iot/air_quality/client.py Dockerfiles/iot/air_quality/air_quality/AirQualityUCI.csv.xz buildstatus/certificates
	$(BUILD_CMD) --file $< --tag iotsim/air-quality Dockerfiles/iot/air_quality
	@touch $@

buildstatus/cooler_motor: Dockerfiles/iot/cooler_motor/Dockerfile Dockerfiles/iot/cooler_motor/client.py Dockerfiles/iot/cooler_motor/accelerometer/accelerometer.csv.xz buildstatus/certificates
	$(BUILD_CMD) --file $< --tag iotsim/cooler-motor Dockerfiles/iot/cooler_motor
	@touch $@

buildstatus/predictive_maintenance: Dockerfiles/iot/predictive_maintenance/Dockerfile Dockerfiles/iot/predictive_maintenance/client.py Dockerfiles/iot/predictive_maintenance/ai4i2020/ai4i2020.csv.xz buildstatus/certificates
	$(BUILD_CMD) --file $< --tag iotsim/predictive-maintenance Dockerfiles/iot/predictive_maintenance
	@touch $@

buildstatus/hydraulic_system: Dockerfiles/iot/hydraulic_system/Dockerfile Dockerfiles/iot/hydraulic_system/client.py Dockerfiles/iot/hydraulic_system/condition_monitoring_hydraulic/*.txt.xz buildstatus/certificates
	$(BUILD_CMD) --file $< --tag iotsim/hydraulic-system Dockerfiles/iot/hydraulic_system
	@touch $@

buildstatus/building_monitor: Dockerfiles/iot/building_monitor/Dockerfile Dockerfiles/iot/building_monitor/client.py Dockerfiles/iot/building_monitor/appliances_energy/energydata_complete.csv.xz buildstatus/certificates
	$(BUILD_CMD) --file $< --tag iotsim/building-monitor Dockerfiles/iot/building_monitor
	@touch $@

buildstatus/domotic_monitor: Dockerfiles/iot/domotic_monitor/Dockerfile Dockerfiles/iot/domotic_monitor/client.py Dockerfiles/iot/domotic_monitor/sml2010/*.txt.xz buildstatus/certificates
	$(BUILD_CMD) --file $< --tag iotsim/domotic-monitor Dockerfiles/iot/domotic_monitor
	@touch $@

buildstatus/coap_server: Dockerfiles/iot/coap_server/Dockerfile Dockerfiles/iot/coap_server/coap-server-mod.c
	$(BUILD_CMD) --file $< --tag iotsim/coap-server Dockerfiles/iot/coap_server
	@touch $@

buildstatus/coap_cloud: Dockerfiles/iot/coap_cloud/Dockerfile Dockerfiles/iot/coap_cloud/coap-client-mod.c Dockerfiles/iot/coap_cloud/coap_cloud.py
	$(BUILD_CMD) --file $< --tag iotsim/coap-cloud Dockerfiles/iot/coap_cloud
	@touch $@

buildstatus/city_power: Dockerfiles/iot/city_power/Dockerfile Dockerfiles/iot/city_power/coap-server-mod.c Dockerfiles/iot/city_power/tetuan_power/TetuanCityPowerConsumption.csv.xz
	$(BUILD_CMD) --file $< --tag iotsim/city-power Dockerfiles/iot/city_power
	@touch $@

buildstatus/city_power_tls: Dockerfiles/iot/city_power/Dockerfile.tls buildstatus/certificates buildstatus/city_power
	$(BUILD_CMD) --file $< --tag iotsim/city-power-tls Dockerfiles/iot/city_power
	@touch $@

buildstatus/combined_cycle: Dockerfiles/iot/combined_cycle/Dockerfile Dockerfiles/iot/combined_cycle/coap-server-mod.c Dockerfiles/iot/combined_cycle/combined_cycle_power_plant/Fold1_pp.csv.xz
	$(BUILD_CMD) --file $< --tag iotsim/combined-cycle Dockerfiles/iot/combined_cycle
	@touch $@

buildstatus/combined_cycle_tls: Dockerfiles/iot/combined_cycle/Dockerfile.tls buildstatus/certificates buildstatus/combined_cycle
	$(BUILD_CMD) --file $< --tag iotsim/combined-cycle-tls Dockerfiles/iot/combined_cycle
	@touch $@

buildstatus/city_power_cloud: Dockerfiles/iot/city_power_cloud/Dockerfile Dockerfiles/iot/city_power_cloud/coap-client-mod.c Dockerfiles/iot/city_power_cloud/coap_cloud.py buildstatus/certificates
	$(BUILD_CMD) --file $< --tag iotsim/city-power-cloud Dockerfiles/iot/city_power_cloud
	@touch $@

buildstatus/combined_cycle_cloud: Dockerfiles/iot/combined_cycle_cloud/Dockerfile Dockerfiles/iot/combined_cycle_cloud/coap-client-mod.c Dockerfiles/iot/combined_cycle_cloud/coap_cloud.py buildstatus/certificates
	$(BUILD_CMD) --file $< --tag iotsim/combined-cycle-cloud Dockerfiles/iot/combined_cycle_cloud
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

