# This script translates MIDI data (already converted to CSVs via MIDICSV) to a Pandas DataFrame with the following information:
# • Timing
# • Note
# • Velocity
# • Player
# • Section of Composition
# • Y-axis value
# • Marimba side
# The dataframe can then be converted to CSV for use in After Effects or left as is for use in Blender.

import pandas as pd
import glob
import os
from BPMtoFPS import *

# -- MUSIC COLUMNS --
# Establish variables for CSV files and names of columns in resulting dataframe.
all_files = sorted(glob.glob(os.path.join(os.path.abspath(os.getcwd()), "CSVs/*.csv")))
names = ['data','time','status','num','note','velocity','ex1','ex2']

# CSV files are combined into DataFrame, with additional "player" column to identify players.
df = pd.concat((pd.read_csv(f, names=names, header=None).assign(player=i + 1)
	for i, f in enumerate(all_files)), ignore_index=True)

df = df[df['status'].str.contains('Note_on_c')] # remove all "note_off_c" instructions and header rows
df = df[['time', 'note', 'velocity', 'player']] # trim dataframe down to appropriate columns
df['time'] = (df['time'] / 240 + 1).astype(int) # simplify time down to eighth notes
df[['note', 'velocity']] = df[['note', 'velocity']].astype(int) # set appropriate columns as integer
df = df.reset_index(drop=True) # Reset the index to reflect the new structure

# Add column for section of composition, this will be used in case environment or shapes vary between them.
# First, Logic Pro 4/4 measure time (328 total measures) has to be converted to MIDI time (240 milliseconds per note).
s1 = (329 - 1) * 4 # end of section I in MIDI time
s2 = (676 - 1) * 4 # end of section II in MIDI time

# Assign sections based on timing to dataframe.
df.loc[df['time'] < s1, 'section'] = 1
df.loc[(df['time'] >= s1) & (df['time'] < s2), 'section'] = 2
df.loc[df['time'] >= s2, 'section'] = 3
df['section'] = df['section'].astype('int') # Convert column to integer

# -- VIDEO COLUMNS --
# Add columns for the position of notes, calculating only y-axis values for After Effects test, and video timecode.

# Set up variables for video size, object size, and limits of note placement based on action-safe zone.
# After Effects compositions put (0,0) in the top left corner of the frame.
total_h = 2160 # height of 4k UHD resolution
as_h = 2160 - 2008 # 2008 is total height of action-safe zone for 4k UHD TVs
ring_size = 1000 # total size of ring at its largest point
shape_range = total_h - as_h - ring_size # total amount of room within which rings can be positioned
shape_edge = total_h - as_h / 2 - ring_size / 2
# The variable shape_edge is the lowest point to where a note can be placed in a video composition.
# To get the highest point, we'll use the formula shape_edge - shape_range later.

# Set up dataframe to hold values for each note on the marimba, with fake notes added so that the index compensates for
# spaces between the groups of sharps and flats on the keyboard. The index can then be used to mathematically
# calculate y-position.
note_min = df['note'].min() # lowest note value of composition
note_max = df['note'].max() # highest note value of composition
note_range = note_max - note_min # full range of notes for composition
keyb_values = [i + note_min for i in range(note_range + 1)] # the list of values going from low to high
keyboard = pd.DataFrame({'key': keyb_values}) # converting the list to a dataframes

# Create a separate dataframe of fake notes.
fake_notes = [52.5, 59.5, 64.5, 71.5, 76.5]
fake_notes_df = pd.DataFrame({'key': fake_notes}) # converting fake notes list to dataframe
keyboard = pd.concat([keyboard, fake_notes_df], ignore_index=True) # combine the two dataframes
keyboard = keyboard.sort_values('key').reset_index(drop=True) # sort the dataframe, reset index
# Resetting the index here is intentional and important because once the fake notes are removed, the index is now
# an accurate replica of a marimba's keyboard, with the spaces between groups of sharps and flats represented by the
# removed fake notes.
keyboard = keyboard[keyboard['key'] % 1 == 0].astype('int') # remove fake notes, change all values back to integers
keyboard = keyboard.reset_index(names='idx') # save the index to its own column, easier to merge with original dataframe

# The keyboard dataframe can now be used as a reference for where notes are going to be placed on the After Effects
# composition. The next step is to update the original dataframe with a "y" column.
merged_keys = df.merge(keyboard, left_on='note', right_on='key', how='left') # merge keyboard and original dataframe
df['y'] = merged_keys['idx'] # the new 'y' column in the original dataframe now has the merged dataframe's data

# Before finishing with the 'y' column, the 'side' column will identify which side of the marimba is being played, in case
# that distinction is made visually in After Effects (adding more realism to the playing).
df['side'] = (df['y'] % 2 == 0)

# The remaining step is to calculate the exact y-axis value that will be used in After Effects. To do this, we need
# the minimum value and maximum value to set a range. Because each section has its own range, we'll do it per section
# and figure out how to transition between them later.
for i in range(1, 4):
	s_note_min = df[df['section'] == i]['y'].min() # lowest note of section
	s_note_max = df[df['section'] == i]['y'].max() # lowest note of section
	s_note_range = s_note_max - s_note_min + 1 # total number of note values
	dist = shape_range / s_note_range # total distance between frames
	df.loc[df['section'] == i, 'y'] = df.loc[df['section'] == i, 'y'] - s_note_min
	# Calculate the new y-axis value: multiply it by distance, and subtract by the shape_edge
	df['y'] = df['y'].astype('float') # convert column for decimal values
	df.loc[df['section'] == i, 'y'] = shape_edge - df.loc[df['section'] == i, 'y'] * dist

df['y'] = df['y'].round(1) # round to the nearest decimal, easier to use in After Effects

# For the last column for timecodes, they are generated from the BPMtoFPS script.
df['timecode'] = BPMtoFPS(df['time'] - 1)
