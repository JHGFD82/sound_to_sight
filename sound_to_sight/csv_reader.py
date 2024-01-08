import json
import os
import csv
from sound_to_sight import Note, Pattern


def parse_midi(filename, section_start_times):
    with open(filename, "r") as csvfile:
        rows = list(csv.reader(csvfile))

        # GRAB METADATA FROM HEADER
        division = None
        tempo = None
        notes_per_bar = None

        for row in rows:
            row = [field.strip() for field in row]

            if row[2] == 'note_on_c':
                # We've reached the note rows, stop metadata extraction
                break

            if row[2] == 'Header':
                division = int(row[5])

            if row[2] == 'Tempo':
                tempo = int(row[3])

            if row[2] == 'Time_signature':
                notes_per_bar = int(row[3])

        # ESTABLISH VARIABLES
        if division and tempo and notes_per_bar:
            bpm = 60000000 / tempo
        else:
            raise ValueError('Incomplete metadata, please check the MIDI CSV file')

        pattern_length = int(division * notes_per_bar)

        # ESTABLISH SECTIONS
        # If no section list has been provided or doesn't start at 1,
        # add 1 to the start times list to account for the first section.
        if not section_start_times or section_start_times[0] != 1:
            section_start_times = [1] + section_start_times

        # ESTABLISH SUPPORTED INSTRUMENTS
        # Define layout file directory
        layout_dir = '/midi_data/visual_layouts/'

        # Read the supported_instruments.json file
        with open('midi_data/supported_instruments.json', 'r') as f:
            supported_instruments = json.load(f)

        # Initialize our dictionaries
        instrument_layout = {}
        layout_coordinates = {}

        # Populate dictionaries
        for layout_file, instruments in supported_instruments.items():
            for instrument in instruments:
                # Map instrument to layout_file
                instrument_layout[instrument] = layout_file

            # Read the layout file
            with open(os.path.join(layout_dir, layout_file), 'r') as f:
                layout = json.load(f)

            # Unpack layout dictionary to MIDI to note coordinate mapping
            layout_coord = {int(list(note.keys())[0]): list(note.values())[0] for note in layout}

            # Map layout file to layout_coord
            layout_coordinates[layout_file] = layout_coord

        # ESTABLISH NOTE INFO
        # Read the midi_info.json file
        with open('midi_data/midi_info.json', 'r') as f:
            midi_info = json.load(f)

        # Initialize the note symbols dictionary
        note_symbols = {int(note["MIDI Note Number"]): note["Note Symbol"] for note in midi_info}

        # ESTABLISH ITERABLE VARIABLES
        patterns = {}  # Initialize patterns dictionary per instrument
        player_measures = []  # Initialize player_measures list
        current_section = 0
        current_measure = 0
        player_instruments = {}  # Dictionary mapping player numbers to instruments
        track_to_player = {}  # Dictionary mapping track to player
        player_number = 1  # Player number to assign
        default_instrument = "keyboard"
        unfinished_patterns = []

        # LOOP THROUGH ROWS
        # Continue looping through the rest of the CSV file
        for row in rows:
            row = [field.strip() for field in row]

            time = int(row[1])
            event_type = row[2]
            track = int(row[0])

            # Condition for instrument declaration
            if event_type in ['Title_t', 'Instrument_name_t']:

                # Assign new player number to new track
                if track not in track_to_player:
                    track_to_player[track] = player_number
                    player_number += 1

                # Get current player number
                player_num = track_to_player[track]

                # Priority given to 'Title_t', but if 'Instrument_name_t' appears first, it will be recorded
                # and only overridden by 'Title_t' if it appears later for the same track
                if row[2] == 'Title_t' or player_num not in player_instruments:
                    # Initialize the dictionary for this player number if it doesn't exist
                    if player_num not in player_instruments:
                        player_instruments[player_num] = {"instrument": "", "layout": ""}

                    player_instruments[player_num]["instrument"] = row[3].lower()

                instrument = player_instruments[player_num]["instrument"]
                if instrument not in instrument_layout:
                    user_instrument = input(f"The instrument '{instrument}' does not have a corresponding layout. "
                                            f"Please input the name of a physical instrument, or press Enter to use "
                                            f"the default layout: ").lower().strip()

                    if user_instrument in instrument_layout.keys():
                        instrument = user_instrument
                    else:
                        instrument = default_instrument

                # Fetch the layout for the instrument and save it in player_instruments
                layout = instrument_layout.get(instrument, default_instrument)
                player_instruments[player_num]["instrument"] = instrument
                player_instruments[player_num]["layout"] = layout

            elif event_type == 'Note_on_c':
                note_value = int(row[4])
                velocity = int(row[5])

                # Calculate measure_time
                measure_time = time % pattern_length

                # Retrieve layout, x, and y for the instrument
                player_num = track_to_player.get(track, 0)
                layout = player_instruments[player_num]["layout"]
                x, y = layout_coordinates[layout].get(note_value,
                                                      (0, 0))  # Default to (0,0) if the note doesn't exist in layout

                # Lookup note name
                note_name = note_symbols.get(note_value)

                # Create note
                note_object = Note(start_time=time, measure_time=measure_time, note_value=note_value, velocity=velocity,
                                   note_name=note_name, layout=layout, x=x, y=y)

                # Add note to appropriate pattern
                unfinished_patterns[-1].add_note(note_object)

            elif event_type == 'Note_off_c':
                note_value = int(row[4])

                # Look up the note in previous patterns, starting from earliest
                for pattern in unfinished_patterns:
                    for note in reversed(pattern.notes):
                        if note.note == note_value and note.length is None:
                            note.length = time - note.start_time
                            # Check if all notes in the pattern have defined length
                            if all(note.length is not None for note in pattern.notes):
                                # Calculate hash and move to patterns if the pattern is new
                                pattern_hash = pattern.calculate_hash(pattern.notes)
                                if pattern_hash not in patterns:
                                    patterns[pattern_hash] = pattern
                                # Remove from unfinished_patterns
                                unfinished_patterns.remove(pattern)
                            break

            # When a new measure starts or a new section begins
            # if condition to check for start of new measure/section:
        # Handle end of measure: finalize patterns, update player measures

        # Finalize patterns for the last measure after the last row

#    return player_measures  # or whatever your master list variable is named
