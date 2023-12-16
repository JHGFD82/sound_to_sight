# import_midi
import pandas as pd


def import_midi(files):
    '''
    A list of files sent to this module will be combined into a Pandas DataFrame.

    All columns are included with the addition of a "player" column that numerically separates one MIDI
    file from another, and each CSV file represented as a single instrument in a musical composition.
    '''

    # Establish variables for CSV files and names of columns in resulting dataframe.
    names = ['data', 'time', 'status', 'num', 'note', 'velocity', 'ex1', 'ex2']

    # CSV files are combined into DataFrame, with additional "player" column to identify players.
    df = pd.concat((pd.read_csv(f, names=names, header=None).assign(player=i + 1)
                    for i, f in enumerate(files)), ignore_index=True)

    return df
