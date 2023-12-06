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
total_h = 2160 # height of 4k UHD resolution
as_h = 2160 - 2008 # 2008 is total height of action-safe zone for 4k UHD TVs
h_edge = total_h / 2 - as_h / 2 # height limit of action-safe zone
ring_size = 1000 # total size of ring at its largest point
shape_edge = h_edge - ring_size / 2 # the limit to where a note can be placed

# Set up dataframe to hold values for each note on the marimba, with fake notes added so that the index compensates for
# upper keys that do not naturally exist on keyboard. The index can then be used to mathematically calculate y-position.
s1_note_min = df[df['section'] == 1]['note'].min() # lowest note value of Section I 
s1_note_max = df[df['section'] == 1]['note'].max() # highest note value of Section I
keyb_values = [i + s1_note_min for i in range(s1_note_max - s1_note_min + 1)]
keyboard = pd.DataFrame({'key': keyb_values})

# Add fake keys.
add_fake = [{'key': 55.5}, {'key': 60.5}, {'key':67.5}, {'key':72.5}]
add_fake_df = pd.DataFrame(add_fake)
keyboard = pd.concat([keyboard, add_fake_df], ignore_index=True)
keyboard = keyboard.sort_values('key').reset_index(drop=True)
keyboard = keyboard[keyboard['key'] % 1 == 0].astype('int')
s1_notes = s1_note_max - s1_note_min # Range of notes across whole composition
df['y'] = df['note'] - note_min

print(df)
