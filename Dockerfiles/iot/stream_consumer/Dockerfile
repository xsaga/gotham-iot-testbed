FROM alpine

RUN apk add ffmpeg python3

COPY consume.py /consume.py
RUN chmod +x /consume.py

ENTRYPOINT [ "/consume.py" ]
