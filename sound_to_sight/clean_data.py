import pandas as pd
from typing import Tuple


def prepare_for_extraction(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare the given DataFrame for extraction by performing the following transformations:

    1. Convert specific columns to numeric data type, coercing non-convertible values to NaN.
    2. Change the 'status' column values by removing leading and trailing whitespaces.
    3. Modify the 'instrument' column values by removing any numeric characters, leading and trailing whitespaces,
       and converting the values to lowercase.

    Parameters:
        df (pandas.DataFrame): The DataFrame to be prepared for extraction.

    Returns:
        pandas.DataFrame: The modified DataFrame with the specified transformations.
    """
    for column in ['time', 'num', 'note', 'velocity', 'extra1', 'extra2', 'player']:
        df[column] = pd.to_numeric(df[column], errors='coerce').astype('Int32')
    df['status'] = df['status'].str.strip()
    df['instrument'] = df['instrument'].str.replace(r'\d+', '', regex=True).str.strip().str.lower()
    return df


def extract_relevant_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, float, int]:
    """
    Extracts relevant data from a dataframe.

    Parameters:
    - df: pandas DataFrame
        The input dataframe containing the musical data.

    Returns:
    - Tuple[pandas DataFrame, float, int]
        A tuple containing the relevant data extracted from the dataframe:
        - First element: A processed dataframe with columns ['time', 'status', 'note', 'velocity', 'player', 'instrument'].
        - Second element: The value of the 'velocity' column from the row with 'status' value as 'Header'.
        - Third element: The value of the 'num' column from the row with 'status' value as 'Time_signature'.

    Raises:
    - ValueError: If the dataframe is missing the 'Header' row or the 'Time_signature' row.
    """
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
