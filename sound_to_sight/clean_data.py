import pandas as pd


def prepare_for_extraction(df):
    for column in ['time', 'num', 'note', 'velocity', 'extra1', 'extra2', 'player']:
        df[column] = pd.to_numeric(df[column], errors='coerce').astype('Int32')
    df['status'] = df['status'].str.strip()
    df['instrument'] = df['instrument'].str.replace(r'\d+', '', regex=True).str.strip().str.lower()
    return df


def extract_relevant_data(df):
    try:
        division = df[df['status'] == "Header"]['velocity'].values[0]
    except IndexError:
        raise ValueError("Dataframe lacks 'Header' row!")
    try:
        notes_per_bar = df[df['status'] == "Time_signature"]['num'].values[0]
    except IndexError:
        raise ValueError("Dataframe lacks 'Time_signature' row!")
    df = df[df['status'].isin(['Note_on_c', 'Note_off_c'])][
        ['time', 'status', 'note', 'velocity', 'player', 'instrument']]
    return df.reset_index(drop=True), division, notes_per_bar


def clean_data(dataframe):
    """
    Clean and process DataFrame

    Parameters:
        dataframe (pandas.DataFrame): DataFrame that needs to be cleaned and processed

    Returns:
        tuple: Tuple with cleaned DataFrame, division and notes_per_bar

    Raises:
        ValueError: If dataframe lacks 'Header' or 'Time_signature' row
    """
    dataframe = prepare_for_extraction(dataframe)
    dataframe, division, notes_per_bar = extract_relevant_data(dataframe)
    return dataframe, division, notes_per_bar
