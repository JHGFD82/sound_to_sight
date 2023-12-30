import numpy as np
import json
import os

INSTRUMENTS_MAPPING_FILE_PATH = "midi_data/supported_instruments.json"


def gather_instruments(instrument_dict):
    """
    Assigns instruments to players based on a mapping file.

    Parameters:
        instrument_dict (dict): Dictionary containing player and instrument information.

    Returns:
        A dictionary mapping players to their assigned instruments.

    Raises:
        KeyError: If an instrument in the reference dictionary does not exist in the mapping file.
    """
    output_dict = {}

    with open(INSTRUMENTS_MAPPING_FILE_PATH) as json_file:
        instrument_data = json.load(json_file)

    # Create a dictionary to map instrument to its key
    instrument_to_key = {instrument: key for key, instruments in instrument_data.items() for instrument in instruments}

    for player, player_data in instrument_dict.items():
        instrument = player_data.get('instrument')
        if instrument not in instrument_to_key:
            raise KeyError(
                f"An instrument in the reference dictionary does not exist in the mapping file: {instrument}")

        # Add player and their instrument to our output dict
        output_dict[player] = instrument_to_key[instrument]

    return output_dict
