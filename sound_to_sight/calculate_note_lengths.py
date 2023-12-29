import pandas as pd


NOTE_ON_STATUS = 'Note_on_c'
NOTE_OFF_STATUS = 'Note_off_c'


def calculate_note_lengths(df):
    """
    This method calculates the lengths of notes in a dataframe.

    Parameters:
    - df: pandas DataFrame
        The dataframe containing MIDI note data. It should have the following columns:
        - 'time': float
            The time at which the MIDI event occurred.
        - 'status': int
            The status code of the MIDI event.
        - 'note': int
            The MIDI note number.

    Returns:
    - df: pandas DataFrame
        The modified dataframe with an additional column 'length' containing the lengths of the notes.

    Example usage:
        df = pd.DataFrame({
            'time': [0.1, 0.3, 0.5, 0.8],
            'status': [NOTE_ON_STATUS, NOTE_ON_STATUS, NOTE_OFF_STATUS, NOTE_ON_STATUS],
            'note': [60, 62, 60, 64]
        })
        df = calculate_note_lengths(df)

    Note: This method assumes that NOTE_ON_STATUS and NOTE_OFF_STATUS are defined as constants.

    """
    note_start_times = {}
    df['length'] = pd.Series([0] * len(df), dtype='Int32')

    def process_note(row):
        time, status, note = row.iloc[0], row.iloc[1], row.iloc[2]
        if status == NOTE_ON_STATUS:
            note_start_times[note] = (time, row.name)
        elif status == NOTE_OFF_STATUS:
            start_note_info = note_start_times.pop(note, None)
            if start_note_info is not None:
                start_note_time, start_note_index = start_note_info
                df.at[start_note_index, 'length'] = time - start_note_time

    df.apply(process_note, axis=1)

    df = df[df['status'] != NOTE_OFF_STATUS].reset_index(drop=True).drop('status', axis=1)

    return df


def add_measure_time(df, division, notes_per_bar):
    ticks_per_pattern = division * notes_per_bar

    df['measure_time'] = pd.Series([0] * len(df), dtype='Int32')
    df['measure_time'] = df['time'] % ticks_per_pattern

    return df
