import json

INSTRUMENTS_MAPPING_FILE_PATH = "midi_data/supported_instruments.json"


def gather_instruments(dataframe):
    """
    Assigns instruments to players based on a mapping file.

    Parameters:
        dataframe (DataFrame): contains player and instrument information.

    Returns:
        A dictionary mapping instruments to their keys.

    Raises:
        KeyError: If an instrument in the reference dictionary does not exist in the mapping file.
    """
    df_copy = dataframe.copy()

    with open(INSTRUMENTS_MAPPING_FILE_PATH) as json_file:
        instrument_data = json.load(json_file)

    # Create a dictionary to map instrument to its key
    instrument_to_key = {instrument: key for key, instruments in instrument_data.items() for instrument in instruments}

    try:
        # Leverage pandas map function for efficient mapping
        df_copy['player_instrument'] = df_copy['instrument'].map(instrument_to_key)
    except KeyError as e:
        raise KeyError(f"An instrument in the dataframe does not exist in the mapping file: {e}")

    return instrument_to_key
