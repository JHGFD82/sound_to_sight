# clean_data
import pandas as pd


def clean_data(df, quantization):
    '''
    Process the DataFrame resulting from the import_midi module.
    '''

    for column in ['time', 'num', 'note', 'velocity', 'ex1', 'ex2', 'player']:
        df[column] = pd.to_numeric(df[column], errors='coerce').astype('Int32')

    df['time'] = (df['time'] / quantization + 1).astype('Int32')  # simplify time, starting at 1
    df = df[['time', 'status', 'note', 'velocity', 'player']].iloc[9:-2, :]
    return df
