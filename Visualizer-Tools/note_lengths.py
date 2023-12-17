# note_lengths


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

    df = df.reset_index(drop=True)  # Reset the index to reflect the new structure

    return df
