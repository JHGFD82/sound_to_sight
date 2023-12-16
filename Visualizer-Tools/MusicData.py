import pandas as pd
import glob
import os
import sys
from BPMtoFPS import *


def note_lengths(df):

	# Initialize the 'length' column
	df['length'] = pd.Series([-1] * len(df), dtype='Int32')

	# Temporary dictionary to store start time of notes
	note_start_times = {}

	# Iterate through the DataFrame
	for index, row in df.iterrows():
		if row['status'] == ' Note_on_c':
			# Store the start time and index of the note
			note_start_times[row['note']] = (row['time'], index)
		elif row['status'] == ' Note_off_c':
			# Retrieve the start time and index
			start_info = note_start_times.pop(row['note'], None)
			if start_info != -1:
				start_time, start_index = start_info
				# Calculate the length and update it at the 'Note_on_c' row
				df.at[start_index, 'length'] = row['time'] - start_time

	# Remove rows with 'Note_off_c'
	df = df[df['status'] != ' Note_off_c']

	df = df.reset_index(drop=True) # Reset the index to reflect the new structure

	return df


def generate_fake_notes(start=4.5, pattern=[7, 5], upper_bound=128):
	current_value = start
	i = 0
	while current_value <= upper_bound:
		yield current_value
		current_value += pattern[i % len(pattern)]
		i += 1


def create_keyboard(df, fake_notes):
	# Create a combined DataFrame of real and fake notes, sorted and cleaned
	note_min, note_max = df['note'].min(), df['note'].max()
	keyb_values = range(note_min, note_max + 1)
	keyboard = pd.DataFrame({'key': list(keyb_values) + fake_notes})

	# Sort, remove fake notes, reset index to align with the marimba's keyboard
	keyboard_dict = (
		keyboard.sort_values('key').reset_index(drop=True)
		.query('key % 1 == 0').reset_index().set_index('key')['index'].astype('Int32')
		.to_dict()
	)

	# Convert keys back to integers
	keyboard_dict = {int(key): val for key, val in keyboard_dict.items()}
	return keyboard_dict


def keyboard_side(df, keyboard):

	# The keyboard dictionary can now be used as a reference for where notes are going to be placed on the After Effects
	# composition. The next step is to update the original dataframe with a "y" column.
	df['y'] = df['note'].map(keyboard)

	# Before finishing with the 'y' column, the 'side' column will identify which side of the marimba is being played, in case
	# that distinction is made visually in After Effects (adding more realism to the playing).
	df['side'] = (df['y'] % 2 == 1)

	return df



df = import_midi([
	'CSVs/Six Marimbas Track 1.csv', 
	'CSVs/Six Marimbas Track 2.csv', 
	'CSVs/Six Marimbas Track 3.csv', 
	'CSVs/Six Marimbas Track 4.csv', 
	'CSVs/Six Marimbas Track 5.csv', 
	'CSVs/Six Marimbas Track 6.csv'
	])
df = clean_data(df)
df = add_sections(df, [1, 329, 676])
df = note_lengths(df)
fake_notes = list(generate_fake_notes())
keyboard = create_keyboard(df, fake_notes)
df = keyboard_side(df, keyboard)

df.to_csv('Six Marimbas Data.csv')

