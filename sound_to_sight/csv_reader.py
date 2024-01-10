import json
import os
import csv
import re
from sound_to_sight import Note, Pattern, PlayerMeasure


def parse_header(rows):
    """Parse the header to extract MIDI file metadata."""
    division, tempo, notes_per_bar = None, None, None
    for row in rows:
        row = [field.strip() for field in row]
        if row[2] == 'note_on_c':
            # Stop metadata extraction when note rows are reached
            break
        if row[2] == 'Header':
            division = int(row[5])
        if row[2] == 'Tempo':
            tempo = int(row[3])
        if row[2] == 'Time_signature':
            notes_per_bar = int(row[3])
    if not (division and tempo and notes_per_bar):
        raise ValueError('Incomplete metadata, please check the MIDI CSV file')
    return division, tempo, notes_per_bar


def calculate_bpm(tempo):
    """Calculate beats per minute from tempo."""
    return 60000000 / tempo


def establish_sections(section_start_times):
    """Establish the sections based on start times."""
    if not section_start_times or section_start_times[0] != 1:
        section_start_times = [1] + section_start_times
    return section_start_times


def load_supported_instruments():
    """Load supported instruments from a JSON file."""
    with open('midi_data/supported_instruments.json', 'r') as f:
        supported_instruments = json.load(f)
    return supported_instruments


def process_unfinished_patterns(measure_number, current_measure, pattern, current_player, player_measures,
                                section_number, instrument, unfinished_patterns, i):
    # Check if this pattern has no unfinished notes
    if measure_number < current_measure and all(
            note.length is not None for note in pattern.notes):
        # Compute hash of completed notes in this pattern
        pattern_hash = pattern.calculate_hash(pattern.notes)
        pattern.hash = pattern_hash
        if current_player not in player_measures:
            player_measures[current_player] = []
            player_measures[current_player].append(PlayerMeasure(
                measure_number, section_number, current_player, instrument, pattern))
        else:
            # Move this pattern to patterns if it's a new unique pattern
            latest_pm = player_measures[current_player][-1]
            if not latest_pm.pattern.hash or pattern_hash != latest_pm.pattern.hash:
                player_measures[current_player].append(PlayerMeasure(
                    measure_number, section_number, current_player, instrument, pattern))
            else:
                latest_pm.play_count += 1

        del unfinished_patterns[i]


def parse_midi(filename, section_start_times):
    with open(filename, "r") as csvfile:
        rows = list(csv.reader(csvfile))

        division, tempo, notes_per_bar = parse_header(rows)
        bpm = calculate_bpm(tempo)
        section_start_times = establish_sections(section_start_times)
        supported_instruments = load_supported_instruments()

        layout_dir = 'midi_data/visual_layouts/'

        # Initialize our dictionaries
        instrument_layout = {}
        layout_coordinates = {}

        # Populate dictionaries
        for layout_file, instruments in supported_instruments.items():
            for instrument in instruments:
                # Map instrument to layout_file
                instrument_layout[instrument] = layout_file

            # Read the layout file and save data to layout_coordinates dictionary
            with open(os.path.join(layout_dir, layout_file), 'r') as f:
                layout = json.load(f)
                layout_coord = {int(key): values for key, values in layout.items()}
                layout_coordinates[layout_file] = layout_coord

        # ESTABLISH NOTE INFO
        # Read the midi_info.json file and save note info to note_symbols
        with open('midi_data/midi_info.json', 'r') as f:
            midi_info = json.load(f)
            note_symbols = {int(note["MIDI Note Number"]): note["Note Symbol"] for note in midi_info}

        # ESTABLISH ITERABLE VARIABLES
        pattern_length = division * notes_per_bar
        player_measures = {}  # Initialize player_measures list
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
                    current_section = 1

                # Get current player number
                current_player = track_to_player[track]

                # Priority given to 'Title_t', but if 'Instrument_name_t' appears first, it will be recorded
                # and only overridden by 'Title_t' if it appears later for the same track
                if row[2] == 'Title_t' or current_player not in player_instruments:
                    # Initialize the dictionary for this player number if it doesn't exist
                    if current_player not in player_instruments:
                        player_instruments[current_player] = {"instrument": "", "layout": ""}

                    instrument = row[3].lower().replace('"', '')
                    player_instruments[current_player]["instrument"] = re.sub(r'\s+-?\d+$', '', instrument)

            elif event_type == 'Note_on_c':

                # Section check
                if current_section < len(section_start_times) and (
                        time / pattern_length >= section_start_times[current_section]):
                    current_section += 1

                # Start the analysis of a new note
                note_value = int(row[4])
                velocity = int(row[5])
                measure_time = time % pattern_length
                current_measure = (time // pattern_length) + 1
                dict_key = (current_player, current_measure, current_section)

                for i, pattern_dict in enumerate(unfinished_patterns):
                    for header_dict, pattern in pattern_dict.items():
                        current_player, measure_number, section_number = header_dict
                        process_unfinished_patterns(measure_number, current_measure, pattern, current_player,
                                                    player_measures, section_number, instrument,
                                                    unfinished_patterns, i)

                # Check if the instrument gathered from the track header rows is in the list of supported instruments
                if not player_instruments[current_player]["layout"]:
                    instrument = player_instruments[current_player]["instrument"]
                    if instrument not in instrument_layout:
                        user_instrument = input(f"The instrument '{instrument}' does not have a corresponding layout. "
                                                f"Please input the name of a physical instrument, or press Enter to "
                                                f"use the default layout: ").lower().strip()

                        if user_instrument in instrument_layout.keys():
                            instrument = user_instrument
                        else:
                            instrument = default_instrument

                    # Fetch the layout for the instrument and save it in player_instruments
                    layout = instrument_layout.get(instrument, default_instrument).replace("_layout.json", "")
                    player_instruments[current_player] = {"instrument": instrument, "layout": layout}
                    unfinished_patterns.append({dict_key: Pattern(instrument)})

                # NEED TO PUT IN LOGIC FOR HANDLING MULTI-RESULT X,Y COORDS (CELLO, VIOLIN)
                x, y = layout_coordinates[layout + '_layout.json'].get(note_value)[0].values()

                # Lookup note name
                note_name = note_symbols.get(note_value)

                # Create note
                note_object = Note(start_time=time, measure_time=measure_time, note_value=note_value, velocity=velocity,
                                   note_name=note_name, layout=layout, x=x, y=y)

                # Add note to appropriate pattern
                if not unfinished_patterns:
                    unfinished_patterns.append({dict_key: Pattern(instrument)})

                unfinished_patterns[-1][dict_key].add_note(note_object)

            elif event_type == 'Note_off_c':
                note_value = int(row[4])
                current_measure = (time // pattern_length) + 1
                all_found = [False, 0]

                # Process incomplete patterns
                for i, pattern_dict in enumerate(unfinished_patterns):
                    for header_dict, pattern in pattern_dict.items():
                        current_player, measure_number, section_number = header_dict
                    # convert dict view to list to be able to delete keys during iteration
                    # Find the corresponding starting note in this pattern, if any
                    for note in reversed(pattern.notes):
                        if note.note_value == note_value and note.length is None:
                            # Found the starting note, set its length
                            note.length = time - note.start_time

                            # Check if this pattern has no unfinished notes
                            if measure_number < current_measure and all(
                                    note.length is not None for note in pattern.notes):
                                # Compute hash of completed notes in this pattern
                                pattern_hash = pattern.calculate_hash(pattern.notes)
                                pattern.hash = pattern_hash
                                if current_player not in player_measures:
                                    player_measures[current_player] = []
                                    player_measures[current_player].append(PlayerMeasure(
                                        measure_number, section_number, current_player, instrument, pattern))
                                else:
                                    # Move this pattern to patterns if it's a new unique pattern
                                    latest_pm = player_measures[current_player][-1]
                                    if not latest_pm.pattern.hash or pattern_hash != latest_pm.pattern.hash:
                                        player_measures[current_player].append(PlayerMeasure(
                                            measure_number, section_number, current_player, instrument, pattern))
                                    else:
                                        latest_pm.play_count += 1

                                all_found = [True, i]

                            break

                if all_found[0]:
                    del unfinished_patterns[all_found[1]]
