import pandas as pd


def clean_data(df):
    """

    Cleans and processes the given DataFrame.

    Parameters:
        df (pandas.DataFrame): The DataFrame containing the data to be cleaned and processed.

    Returns:
        tuple: A tuple containing the cleaned DataFrame, the division value extracted from the DataFrame,
            and the notes per bar value extracted from the DataFrame.

    Raises:
        ValueError: If the DataFrame is missing a 'Header' row or a 'Time_signature' row.

    """
    def prep_for_extraction(dataframe):
        for column in ['time', 'num', 'note', 'velocity', 'extra1', 'extra2', 'player']:
            dataframe[column] = pd.to_numeric(dataframe[column], errors='coerce').astype('Int32')
        dataframe['status'] = dataframe['status'].str.strip()
        dataframe['instrument'] = dataframe['instrument'].str.replace(r'\d+', '', regex=True).str.strip().str.lower()
        return dataframe

    def extract_relevant_data(dataframe):
        try:
            division_extract = dataframe[dataframe['status'] == "Header"]['velocity'].values[0]
        except IndexError:
            raise ValueError("The DataFrame is missing a 'Header' row!")

        try:
            notes_per_bar_extract = dataframe[dataframe['status'] == "Time_signature"]['num'].values[0]
        except IndexError:
            raise ValueError("The DataFrame is missing a 'Time_signature' row!")

        valid_statuses = ['Note_on_c', 'Note_off_c']
        dataframe_filtered = dataframe[dataframe['status'].isin(valid_statuses)][
            ['time', 'status', 'note', 'velocity', 'player', 'instrument']]

        dataframe_filtered = dataframe_filtered.reset_index(drop=True)

        return dataframe_filtered, division_extract, notes_per_bar_extract

    df = prep_for_extraction(df)
    df, division, notes_per_bar = extract_relevant_data(df)

    return df, division, notes_per_bar
