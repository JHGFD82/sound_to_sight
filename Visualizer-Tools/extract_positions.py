import pandas as pd
import numpy as np
import json
import os
from tqdm import tqdm


def extract_positions(df, layouts, chunk_size=100):
    def find_closest_position(current_note_positions, prev_position):
        if not current_note_positions or prev_position is None:
            return None
        distances = [
            np.linalg.norm(np.array([pos['x'], pos['y']]) - np.array([prev_position['x'], prev_position['y']]))
            for pos in current_note_positions]
        return current_note_positions[np.argmin(distances)]

    def process_chunk(chunked, layout_list, prev_position=None):

        def process_row(per_row, p_position):
            player = per_row['player']
            note = per_row['note']
            layout_file = layout_list.get(player)
            per_position = {'x': None, 'y': None}

            if layout_file:
                layout_path = os.path.join('midi_data/visual_layouts', layout_file)
                if os.path.exists(layout_path):
                    with open(layout_path, 'r') as f:
                        layout = json.load(f)

                    note_positions = [entry[str(note)] for entry in layout if str(note) in entry]
                    if note_positions:
                        if 'keyboard' in layout_file:
                            per_position = note_positions[0]
                        elif 'violin' in layout_file:
                            per_position = find_closest_position(note_positions, p_position)

            return per_position, per_position

        updated_positions = []
        for index, row in chunked.iterrows():
            position, prev_position = process_row(row, prev_position)
            updated_positions.append([position.get('x'), position.get('y')])

        return pd.DataFrame(updated_positions, columns=['x', 'y']), prev_position

    chunks = [df[i:i + chunk_size] for i in range(0, len(df), chunk_size)]
    processed_chunks = []
    previous_position = None

    for chunk in tqdm(chunks):
        processed_chunk, previous_position = process_chunk(chunk, layouts, previous_position)
        processed_chunks.append(processed_chunk)

    results = pd.concat(processed_chunks, ignore_index=True)
    df[['x', 'y']] = results
    return df
