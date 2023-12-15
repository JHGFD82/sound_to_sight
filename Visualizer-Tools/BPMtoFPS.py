import math
import pandas as pd

def BPMtoFPS(series):
	'''Used for converting BPM into timecode.'''

	bpm = 192 # beats per minute
	notes = bpm * 2 # a "beat" is one quarter note, therefore double it to establish
					# eighth notes per minute
	spm = 60 # seconds per minute
	fps = 30 # video frames per second
	duration = 18 # the number of timecodes to calculate from 0:00

	# The timecode is constructed in two processes, based off an initial calculation.
	# The iterable number in this for loop represents each eighth note.
	# The calculation takes the number of eighth notes that can appear in one second of video,
	# then divides the current eighth note into that number to get the fraction of a second
	# where this note appears. The decimal doesn't help yet, but the integer does, because
	# that's the left part of the time code (the "seconds"). The right part is calculated
	# by taking the fraction, keeping only the decimal and multiplying it by 30 to get the
	# specific frame within the second to display the note.

	# Example: Note 16
	# 16 / (384/60=6.4 notes per second) = 2.5, so 2 is the seconds (2:##).
	# 2.5 % 1 = 0.5, and 0.5 * 30 = 15, so 15 is the frame (#:15).
	# Combine both parts: eighth note 16 occurs at 2:15, or two seconds and fifteen frames.
	# If the decimal isn't clean, like for note 15 where the frame would be 10.3125,
	# use the floor module from the math package to make the number a clean integer of 10.

	if not isinstance(series, pd.Series):
		raise ValueError("Input must be a pandas Series.")

	frame = series / (notes / spm)
	return frame.apply(lambda x: str(math.floor(x)) + ':' + f"{math.floor(x % 1 * fps):02d}")
