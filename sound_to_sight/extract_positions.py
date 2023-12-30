import os
import json

LAYOUTS_DIR = 'midi_data/visual_layouts/'


def extract_positions(pattern_details, layouts_dir=LAYOUTS_DIR):
    for instrument, instrument_patterns in pattern_details.items():
        # Load the corresponding layout file
        layout_file = os.path.join(layouts_dir, instrument + "_layout.json")
        with open(layout_file) as file:
            layout_list = json.load(file)
            layout = {list(item.keys())[0]: list(item.values())[0] for item in layout_list}

        # Add x, y coordinates to each note in each pattern
        for pattern in instrument_patterns:
            for i, note in enumerate(pattern['notes']):
                note = list(note)  # Convert tuple to list
                note_value = note[1]  # The second value in the note is the note value
                if str(note_value) in layout:
                    note.append(tuple(layout[str(note_value)].values()))
                pattern['notes'][i] = tuple(note)  # Convert back to tuple and replace the original note

    return pattern_details
