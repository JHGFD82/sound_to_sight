import pandas as pd
import numpy as np
import json
import os
from tqdm import tqdm

INSTRUMENTS_MAPPING_FILE_PATH = "midi_data/supported_instruments.json"


def assign_instrument_json(dataframe):
    """
    Assigns instruments to players based on a mapping file.

    Parameters:
        dataframe (pandas.DataFrame): Pandas DataFrame containing player and instrument information.

    Returns:
        A dictionary mapping players to their assigned instruments.

    Raises:
        KeyError: If an instrument in the dataframe does not exist in the mapping file, or if the provided
        dataframe is missing the required 'player' column.
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

    # Convert 'player' and 'player_instrument' columns to dictionary
    try:
        player_to_instrument = df_copy.set_index('player')['player_instrument'].to_dict()
    except KeyError as e:
        raise KeyError(f"The provided dataframe is missing required 'player' columns: {e}")

    return player_to_instrument


def extract_positions(df, layouts, chunk_size=100):
    def find_closest_position(current_note_positions, prev_position):
        if not current_note_positions or prev_position is None:
            return None
        distances = [
            np.linalg.norm(np.array([pos['x'], pos['y']]) - np.array([prev_position['x'], prev_position['y']]))
            for pos in current_note_positions]
        return current_note_positions[np.argmin(distances)]

    def process_chunk(chunk, layout_list, prev_position=None):

        def process_row(row, p_position):
            player = row['player']
            note = row['note']
            layout_file = layout_list.get(player)
            position = {'x': None, 'y': None}

            if layout_file:
                layout_path = os.path.join('midi_data/visual_layouts', layout_file)
                if os.path.exists(layout_path):
                    with open(layout_path, 'r') as f:
                        layout = json.load(f)

                    note_positions = [entry[str(note)] for entry in layout if str(note) in entry]
                    if note_positions:
                        if 'keyboard' in layout_file:
                            position = note_positions[0]
                        elif 'violin' in layout_file:
                            position = find_closest_position(note_positions, p_position)

                else:
                    raise FileNotFoundError(f"Layout file {layout_file} not found at {layout_path}")

            # Return the calculated position and the same position to be used as previous position
            return position, position

        updated_positions = []
        for index, row in chunk.iterrows():
            position, prev_position = process_row(row, prev_position)
            updated_positions.append([position.get('x'), position.get('y')])

        return pd.DataFrame(updated_positions, columns=['x', 'y']), prev_position

    chunks = [df[i:i + chunk_size] for i in range(0, len(df), chunk_size)]
    processed_chunks = []
    previous_position = None

    for chunk in tqdm(chunks, leave=False, desc='Setting note positions', color='blue'):
        processed_chunk, previous_position = process_chunk(chunk, layouts, previous_position)
        processed_chunks.append(processed_chunk)

    results = pd.concat(processed_chunks, ignore_index=True)
    df[['x', 'y']] = results
    return df
