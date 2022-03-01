# Needs CAP_SYS_TIME,
# GNS3 runs it correctly

FROM alpine

RUN apk add --no-cache chrony

COPY chrony.conf /etc/chrony/chrony.conf

ENTRYPOINT [ "/usr/sbin/chronyd", "-d" ]

