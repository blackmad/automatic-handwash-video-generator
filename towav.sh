#!/bin/sh

MP3=$@
WAV=${MP3/mp3/wav}
echo $WAV

ffmpeg -i "$@" "$WAV"
