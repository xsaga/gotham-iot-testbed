Video from https://www.pexels.com/video/a-street-in-london-on-a-rainy-night-3037295/

$ ffprobe video.mp4
ffprobe version 4.4.1 Copyright (c) 2007-2021 the FFmpeg developers
  built with gcc 10.3.0 (GCC)
  configuration: --disable-static --prefix=/nix/store/mhiljxkjwlviixyksia2cizczbrn9vk9-ffmpeg-4.4.1 --arch=x86_64 --target_os=linux --enable-gpl --enable-version3 --enable-shared --enable-pic --enable-libsrt --enable-runtime-cpudetect --enable-hardcoded-tables --enable-pthreads --disable-w32threads --disable-os2threads --enable-network --enable-pixelutils --enable-ffmpeg --disable-ffplay --enable-ffprobe --enable-avcodec --enable-avdevice --enable-avfilter --enable-avformat --enable-avresample --enable-avutil --enable-postproc --enable-swresample --enable-swscale --disable-doc --enable-libass --enable-bzlib --enable-gnutls --enable-fontconfig --enable-libfreetype --enable-libmp3lame --enable-iconv --enable-libtheora --enable-libssh --enable-vaapi --enable-libdrm --enable-vdpau --enable-libvorbis --enable-libvpx --enable-lzma --disable-opengl --disable-libmfx --disable-libaom --enable-libpulse --enable-sdl2 --enable-libsoxr --enable-libx264 --enable-libxvid --enable-zlib --enable-libopus --enable-libspeex --enable-libx265 --enable-libdav1d --disable-debug --enable-optimizations --disable-extra-warnings --disable-stripping
  libavutil      56. 70.100 / 56. 70.100
  libavcodec     58.134.100 / 58.134.100
  libavformat    58. 76.100 / 58. 76.100
  libavdevice    58. 13.100 / 58. 13.100
  libavfilter     7.110.100 /  7.110.100
  libavresample   4.  0.  0 /  4.  0.  0
  libswscale      5.  9.100 /  5.  9.100
  libswresample   3.  9.100 /  3.  9.100
  libpostproc    55.  9.100 / 55.  9.100
Input #0, mov,mp4,m4a,3gp,3g2,mj2, from 'video.mp4':
  Metadata:
    major_brand     : mp42
    minor_version   : 0
    compatible_brands: mp42mp41isomavc1
    creation_time   : 2019-10-06T01:03:46.000000Z
  Duration: 00:00:39.55, start: 0.000000, bitrate: 5832 kb/s
  Stream #0:0(und): Video: h264 (High) (avc1 / 0x31637661), yuv420p(tv, bt709), 1920x1080, 5576 kb/s, 29.97 fps, 29.97 tbr, 30k tbn, 60k tbc (default)
    Metadata:
      creation_time   : 2019-10-06T01:03:46.000000Z
      handler_name    : L-SMASH Video Handler
      vendor_id       : [0][0][0][0]
      encoder         : AVC Coding
  Stream #0:1(und): Audio: aac (LC) (mp4a / 0x6134706D), 48000 Hz, stereo, fltp, 253 kb/s (default)
    Metadata:
      creation_time   : 2019-10-06T01:03:46.000000Z
      handler_name    : L-SMASH Audio Handler
      vendor_id       : [0][0][0][0]
