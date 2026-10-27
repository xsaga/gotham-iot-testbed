FROM ubuntu:focal

RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y openssl


WORKDIR /artifacts/psk

RUN openssl rand -hex -out psk.txt 8

WORKDIR /artifacts/pki

# https://mosquitto.org/man/mosquitto-tls-7.html
RUN openssl rand -hex -out ca_password 8 &&\
    openssl req -new -x509 -days 365 -extensions v3_ca -passout file:ca_password -keyout iot-sim-ca.key -out iot-sim-ca.crt \
    -subj "/C=US/ST=Massachusetts/L=Innsmouth/O=IoT Sim/OU=Certificate Authority/" &&\
    openssl genrsa -out server.key 2048 &&\
    openssl req -out server.csr -key server.key -new \
    -subj "/C=US/ST=Massachusetts/L=Innsmouth/O=IoT Sim/OU=Servers/CN=secure.mqtt.lab/" &&\
    openssl x509 -req -in server.csr -CA iot-sim-ca.crt -CAkey iot-sim-ca.key -CAcreateserial -passin file:ca_password -out server.crt -days 180

WORKDIR /artifacts

CMD ["/usr/bin/openssl", "version"]
