import pandas as pd


NOTE_ON_STATUS = 'Note_on_c'
NOTE_OFF_STATUS = 'Note_off_c'


def calculate_note_lengths(df):
    note_start_times = {}
    df['length'] = pd.Series([0] * len(df), dtype='Int32')

    def process_note(row):
        time, status, note = row[1], row[2], row[3]
        if status == NOTE_ON_STATUS:
            note_start_times[note] = (time, row.name)
        elif status == NOTE_OFF_STATUS:
            start_note_info = note_start_times.pop(note, None)
            if start_note_info is not None:
                start_note_time, start_note_index = start_note_info
                df.at[start_note_index, 'length'] = time - start_note_time

    df.apply(process_note, axis=1)

    df = df[df['status'] != NOTE_OFF_STATUS].reset_index(drop=True)
    return df
