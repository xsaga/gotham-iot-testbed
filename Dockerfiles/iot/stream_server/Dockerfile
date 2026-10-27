# using directly aler9/rtsp-simple-server fails ing GN3 for some reason...

FROM alpine AS rtsp
RUN wget -qO- https://github.com/bluenviron/mediamtx/releases/download/v0.18.3/rtsp-simple-server_v0.18.3_linux_amd64.tar.gz \
    | tar xz -C /

FROM alpine
COPY --from=rtsp /rtsp-simple-server /
COPY rtsp-simple-server.yml /
ENTRYPOINT [ "/rtsp-simple-server" ]
