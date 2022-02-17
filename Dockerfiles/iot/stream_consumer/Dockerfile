FROM alpine

RUN apk add --no-cache ffmpeg python3

COPY consume.py /consume.py
RUN chmod +x /consume.py

ENTRYPOINT [ "/consume.py" ]
