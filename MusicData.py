import pandas as pd
import glob
import os

all_files = sorted(glob.glob(os.path.join(os.path.abspath(os.getcwd()), "*.csv")))
names = ['data','time','status','num','note','velocity','ex1','ex2']
df = pd.concat((pd.read_csv(f, names=names, header=None).assign(midi=i+1) for i, f in enumerate(all_files)), ignore_index=True)
df = df[df['status'].str.contains('Note_on_c')]
df['note'] = df['note'].astype(int)
df['velocity'] = df['velocity'].astype(int)
df = df[['time', 'note', 'velocity', 'midi']]
df = df.reset_index(drop=True)
print(df)
