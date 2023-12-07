import pandas as pd
import glob
import os

# Establish variables for CSV files and names of columns in resulting DataFrame.
all_files = sorted(glob.glob(os.path.join(os.path.abspath(os.getcwd()), "CSVs/*.csv")))
names = ['data','time','status','num','note','velocity','ex1','ex2']

# CSV files are combined into DataFrame, with additional "midi" column to identify players.
df = pd.concat((pd.read_csv(f, names=names, header=None).assign(midi=i+1) for i, f in enumerate(all_files)), ignore_index=True)

# For scripting purposes, remove all "note_off_c" instructions and header rows.
df = df[df['status'].str.contains('Note_on_c')]

# Ensure note and velocity columns are set to integer type.
df['note'] = df['note'].astype(int)
df['velocity'] = df['velocity'].astype(int)

# Keep timing, note pitch, note velocity, and player columns.
df = df[['time', 'note', 'velocity', 'midi']]

# Reset the DataFrame index to reflect the new structure.
df = df.reset_index(drop=True)

# Add column for section of composition, this will be used in case environment or shapes vary between them.
# First, Logic Pro 4/4 measure time (328 total measures) has to be converted to MIDI time (240 milliseconds per note).
s1 = (329 - 1) * 4 * 240 # end of section I in MIDI time
s2 = (676 - 1) * 4 * 240 # end of section II in MIDI time

# Assign sections based on timing to dataframe.
df.loc[df['time'] < s1, 'section'] = int(1)
df.loc[(df['time'] >= s1) & (df['time'] < s2), 'section'] = int(2)
df.loc[df['time'] >= s2, 'section'] = int(3)
df['section'] = df['section'].astype('int') # Convert column to integer

# -- NOTE POSITION --
# Add columns for the position of notes, calculating only y values for After Effects test.

# Set up variables for video size, object size, and limits of note placement based on action-safe zone.
# After Effects compositions put (0,0) in the center of the frame. Therefore, we will need to divide results by 2
# so the highest placement is the variable we'll make here, and the lowest placement is that variable as negative.
total_h = 2160 # height of 4k UHD resolution
as_h = 2160 - 2008 # 2008 is total height of action-safe zone for 4k UHD TVs
h_edge = total_h / 2 - as_h / 2 # height limit of action-safe zone
ring_size = 1000 # total size of ring at its largest point
shape_edge = h_edge - ring_size / 2 # the limit to where a note can be placed

# Set up dataframe to hold values for each note on the marimba, with fake notes added so that the index compensates for
# upper keys that do not naturally exist on keyboard. The index can then be used to mathematically calculate y-position.
note_min = df['note'].min() # lowest note value of composition
note_max = df['note'].max() # highest note value of composition
note_range = note_max - note_min # full range of notes for composition
keyb_values = [i + note_min for i in range(note_range + 1)] # the list of values going from low to high
keyboard = pd.DataFrame({'key': keyb_values}) # converting the list to a dataframe

# Create a separate dataframe of fake notes.
fake_notes = [55.5, 60.5, 67.5, 72.5, 79.5]
fake_notes_df = pd.DataFrame({'key': fake_notes}) # converting fake notes list to dataframe
keyboard = pd.concat([keyboard, fake_notes_df], ignore_index=True) # combine the two dataframes
keyboard = keyboard.sort_values('key').reset_index(drop=True) # sort the dataframe, reset index
# Resetting the index here is intentional and important because once the fake notes are removed, the index is now
# an accurate replica of a marimba's keyboard, with the spaces between groups of upper keys represented by the removed
# fake notes.
keyboard = keyboard[keyboard['key'] % 1 == 0].astype('int') # remove fake notes, change all values back to integers
keyboard = keyboard.reset_index(names='idx') # save the index to its own column, easier to merge with original dataframe

# The keyboard dataframe can now be used as a reference for where notes are going to be placed on the After Effects
# composition. The next step is to update the original dataframe with a "y" column.
merged_keys = df.merge(keyboard, left_on='note', right_on='key', how='left') # merge keyboard values into the dataframe
df['y'] = merged_keys['idx'] # the new 'y' column will take its data from the resulting merged dataframe

# Before finishing with the 'y' column, the 'side' column will identify which side of the marimba is being played, in case
# that distinction is made visually in After Effects (adding more realism to the playing).
df['side'] = (df['y'] % 2 == 0).replace({True: 0, False: 50})

# The remaining step is to calculate the exact y-axis value that will be used in After Effects. To do this, we need
# the minimum value and maximum value to set a range. Because each section has its own range, we'll do it per section
# and figure out how to transition between them later.
for i in range(1, 4):
	s_note_min = df[df['section'] == i]['y'].min() # lowest note of section
	s_note_max = df[df['section'] == i]['y'].max() # lowest note of section
	s_note_range = s_note_max - s_note_min + 1 # total number of note values
	dist = shape_edge * 2 / s_note_range # total distance between frames
	selected_rows = df.loc[df['section'] == i] # grab the rows of this section
	# Calculate the new y-axis value: multiply it by distance, and subtract by the shape_edge so that center is (0,0)
	df.loc[df['section'] == i, 'y'] = selected_rows['y'] * dist + shape_edge 

df['y'] = df['y'].round(1) # round to the nearest decimal, easier to use in After Effects
