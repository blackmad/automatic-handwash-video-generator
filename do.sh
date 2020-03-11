#!/bin/sh

rm *mp4
rm *wav
rm part.mp3

IN=$@
OUT=${IN/mp3/mp4}

set -ex

ffmpeg -i "$@" full.wav
./clever-thumbnailer/src/clever-thumbnailer -l 30 -f 0 full.wav part.wav
python ./downbeats.py part.wav
# lame part.wav
ffmpeg -i out.mp4 -i short.mp3 -c copy -map 0:v:0 -map 1:a:0 tmp.mp4 >& /dev/null

ffmpeg -i tmp.mp4 -c:v libx264  "$OUT"
open -a VLC "$OUT"