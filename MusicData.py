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

print(df)
