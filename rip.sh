#!/bin/sh

WEBM=`youtube-dl --get-filename -x --audio-format mp3 "$@"`
MP3=${WEBM/webm/mp3}

echo $MP3
youtube-dl -x --audio-format mp3 "$@"
./do.sh "$MP3"
