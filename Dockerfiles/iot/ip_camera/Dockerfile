FROM alpine

RUN apk add ffmpeg
COPY video.mp4 /original.mp4

# ffmpeg
# -an      : remove audio
# -r       : set frame rate in fps
# -s:v     : set video frame size wxh
# -codec:v : video format
RUN ffmpeg -i /original.mp4 -an -r 15 -s:v 1280x720 -codec:v libx265 /video.mp4 &&\
    rm -f /original.mp4 &&\
    ffprobe /video.mp4 &&\
    ls -lh /video.mp4

ENTRYPOINT [ "/bin/sh" ]

