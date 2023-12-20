import json
import pandas as pd

INSTRUMENTS_MAPPING_FILE_PATH = "midi_data/supported_instruments.json"


def assign_instrument_json(dataframe):
    df_copy = dataframe.copy()

    with open(INSTRUMENTS_MAPPING_FILE_PATH) as json_file:
        data = json.load(json_file)

    # Create a dictionary to map instrument to its key
    instrument_to_key = {instrument: key for key, instruments in data.items() for instrument in instruments}

    try:
        # Leverage pandas map function for efficient mapping
        df_copy['player_instrument'] = df_copy['instrument'].map(instrument_to_key)
    except KeyError as e:
        raise KeyError(f"An instrument in the dataframe does not exist in the mapping file: {e}")

    # Convert 'player' and 'player_instrument' columns to dictionary
    try:
        player_to_instrument = df_copy.set_index('player')['player_instrument'].to_dict()
    except KeyError as e:
        raise KeyError(f"The provided dataframe is missing required 'player' columns: {e}")

    return player_to_instrument
