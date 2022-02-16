# using directly aler9/rtsp-simple-server fails ing GN3 for some reason...
FROM aler9/rtsp-simple-server AS rtsp

FROM alpine
COPY --from=rtsp /rtsp-simple-server /
COPY rtsp-simple-server.yml /
ENTRYPOINT [ "/bin/sh" ]
