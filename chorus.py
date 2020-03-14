#!/usr/bin/python

import sys
print('initting pychorus')
from pychorus import find_and_output_chorus
print('done')

print(sys.argv)

chorus_start_sec = find_and_output_chorus(sys.argv[1], 'out.wav', 22)
