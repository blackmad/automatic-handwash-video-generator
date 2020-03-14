#!/usr/bin/python
import librosa
import numpy as np
import sys

NUM_IMAGES = 13

from os import listdir
from os.path import isfile, join
mypath = './images'
images = sorted([join(mypath, f) for f in listdir(mypath) if isfile(join(mypath, f))])
print(images)

y, sr = librosa.load(sys.argv[1])
# get onset envelope
onset_env = librosa.onset.onset_strength(y, sr=sr, aggregate=np.median)
# get tempo and beats
tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
print(tempo)
print(beats)
print(len(beats))

beatInterval = int(len(beats) / NUM_IMAGES)
print('beatInterval', beatInterval)

def find_downbeats():
  # we assume 4/4 time
  meter = 4
  # calculate number of full measures 
  measures = (len(beats) // meter)
  # get onset strengths for the known beat positions
  # Note: this is somewhat naive, as the main strength may be *around*
  #       rather than *on* the detected beat position. 
  beat_strengths = onset_env[beats]
  # make sure we only consider full measures
  # and convert to 2d array with indices for measure and beatpos
  measure_beat_strengths = beat_strengths[:measures * meter].reshape(-1, meter)
  # add up strengths per beat position
  beat_pos_strength = np.sum(measure_beat_strengths, axis=0)
  # find the beat position with max strength
  downbeat_pos = np.argmax(beat_pos_strength)
  # convert the beat positions to the same 2d measure format
  full_measure_beats = beats[:measures * meter].reshape(-1, meter)
  # and select the beat position we want: downbeat_pos
  downbeat_frames = full_measure_beats[:, downbeat_pos]
  print('Downbeat frames: {}'.format(downbeat_frames))
  # print times
  downbeat_times = librosa.frames_to_time(downbeat_frames, sr=sr)
  print('Downbeat times in s: {}'.format(downbeat_times))
  return downbeat_times

format = 'MP4V'

from cv2 import VideoWriter, VideoWriter_fourcc, imread, resize
fourcc = VideoWriter_fourcc(*format)
vid = None

import soundfile as sf
f = sf.SoundFile(sys.argv[1])
print('samples = {}'.format(len(f)))
print('sample rate = {}'.format(f.samplerate))
print('seconds = {}'.format(len(f) / f.samplerate))
WAV_LENGTH = len(f) / f.samplerate

FPS = 30

image1 = imread(images[0])
size = image1.shape[1], image1.shape[0]
vid = VideoWriter('out.mp4', fourcc, float(FPS), size, True)

FIRST_BEAT = beats[0]

BEATS_PER_SECOND = (tempo/60)
BEATS_PER_FRAME = BEATS_PER_SECOND / FPS

## good one
# from pydub import AudioSegment
# song = AudioSegment.from_wav(sys.argv[1])
# SECONDS_NEEDED = ((FIRST_BEAT/FPS) + (BEATS_PER_SECOND*NUM_IMAGES)) + 2
# print(f'only need {SECONDS_NEEDED} of {WAV_LENGTH}')
# song = song[:(SECONDS_NEEDED*1000)].fade_out(500)
# song.export("short.mp3", format="mp3")

# FRAMES = int(SECONDS_NEEDED*FPS)
# currentImage = resize(imread('black.png'), size)
# for f in range(0, FIRST_BEAT):
#   print(f)
#   vid.write(currentImage)
# lastBeat = -1
# for frame in range(FIRST_BEAT, int(SECONDS_NEEDED*FPS)):
#   t = frame / FPS
#   beat = int(t / BEATS_PER_SECOND)
#   print(f'frame {frame}, time {t}, beat {beat}, lastBeat {lastBeat}')
#   if beat != lastBeat:
#     lastBeat = beat
#     if (beat < len(images)):
#       print('switching to', images[beat])
#       currentImage = resize(imread(images[beat]), size)
#   vid.write(currentImage)


## with downbeats 

from pydub import AudioSegment
song = AudioSegment.from_wav(sys.argv[1])

downbeats = [0,] + find_downbeats()
print('downbeats:', downbeats)

SECONDS_NEEDED = WAV_LENGTH
if len(downbeats) < 13:
  new_downbeats = []
  for i in range(0, len(downbeats) -1 ):
    new_downbeats.append(downbeats[i])
    new_downbeats.append(downbeats[i] + ((downbeats[i+1]-downbeats[i])/2))
  print('new downbeats: ', new_downbeats)
  downbeats = new_downbeats

if len(downbeats) > 14:
  SECONDS_NEEDED = downbeats[14] + 0.5
print(f'only need {SECONDS_NEEDED} of {WAV_LENGTH}')
song = song[:(SECONDS_NEEDED*1000)].fade_out(500)
song.export("short.mp3", format="mp3")

lastTime = 0
for (index,beatTime) in enumerate(downbeats[:14]):
  if index >= NUM_IMAGES:
    index = NUM_IMAGES
  if index == 0:
    imageFile = 'black'
    currentImage = resize(imread('black.png'), size)
  else:
    imageFile = images[index - 1]
    currentImage = resize(imread(imageFile), size)
  print("reading image, ", imageFile)
  startFrame = int(lastTime * FPS)
  endFrame = int(beatTime * FPS)
  lastTime = beatTime
  for frame in range(startFrame, endFrame):
    # print(f'Frame {frame} = {imageFile}')
    vid.write(currentImage)




# filteredBeats = [beats[i*beatInterval] for i in range(0, NUM_IMAGES+1)]
# print(filteredBeats)
# nextIndex = 1
# for f in range(0, FRAMES):
#   if f < filteredBeats[nextIndex]:
#     vid.write(currentImage)
#   else:
#     print(nextIndex-1)
#     print('switching to ', images[nextIndex-1])
#     currentImage = resize(imread(images[nextIndex-1]), size)
#     nextIndex += 1
#     vid.write(currentImage)


#     if size[0] != img.shape[1] and size[1] != img.shape[0]:
#         img = resize(img, size)
#     vid.write(img)
# vid.release()
#   return vi


