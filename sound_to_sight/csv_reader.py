import json
import os
import csv
import re
from sound_to_sight import Note, Pattern


class MidiCsvParser:
    MICROSECONDS_PER_MINUTE = 60000000

    def __init__(self, filename, fps, section_start_times):
        self.filename = filename
        self.fps = fps

        # Initialize attributes to store MIDI file metadata
        self.division = None
        self.tempo = None
        self.notes_per_bar = None

        # Initialize current placement in row examination
        self.current_player = None
        self.current_measure = 1
        self.current_section = 0

        # Initialize data structures for parsing and processing
        self.player_measures = {}  # To store measures associated with each player
        self.unfinished_patterns = {}  # To keep track of unfinished musical patterns
        self.supported_instruments = {}  # To store information about supported instruments
        self.instrument_layout = {}  # To store layout information for each instrument
        self.layout_coordinates = {}  # To store coordinates for each instrument layout
        self.note_symbols = {}  # To map MIDI note numbers to symbols
        self.section_start_times = section_start_times  # To manage different sections in the music
        self.player_instruments = {}  # Maps player numbers to instruments
        self.track_to_player = {}  # Maps track numbers to player numbers
        self.player_number = 1  # Initial player number
        self.default_instrument = "keyboard"  # Default instrument in case of missing data
        self.pattern_length = None  # Initialize pattern_length

    def parse(self):
        # Open and read the CSV file
        with open(self.filename, "r") as csvfile:
            rows = list(csv.reader(csvfile))

        # Parse the header to extract MIDI file metadata
        self._parse_header(rows)

        # Validate section start time input
        self.establish_sections()

        # Load additional resources necessary for parsing
        self.supported_instruments = self._load_supported_instruments()
        self._initialize_instrument_layouts()

        # Read additional MIDI info if required
        self.note_symbols = self._load_midi_info()

        # Main loop to process each row in the CSV file
        for row in rows:
            self._process_row(row)

        # Return the final result after parsing
        return self.player_measures

    def _initialize_instrument_layouts(self):
        """Loads instrument layout information."""
        # Load supported instruments first
        self.supported_instruments = self._load_supported_instruments()
        layout_dir = 'midi_data/visual_layouts/'

        # Populate the instrument_layout and layout_coordinates dictionaries
        for layout_file, instruments in self.supported_instruments.items():
            # Map each instrument to its corresponding layout file
            for instrument in instruments:
                self.instrument_layout[instrument] = layout_file

            # Load layout coordinates from the layout file
            with open(os.path.join(layout_dir, layout_file), 'r') as f:
                layout = json.load(f)
                layout_coord = {int(key): values for key, values in layout.items()}
                self.layout_coordinates[layout_file] = layout_coord

    def _load_supported_instruments(self):
        """Load supported instruments from a JSON file."""
        with open('midi_data/supported_instruments.json', 'r') as f:
            return json.load(f)

    def _load_midi_info(self):
        """Loads MIDI information from a JSON file."""
        midi_info_file = 'midi_data/midi_info.json'  # Path to the MIDI info JSON file
        with open(midi_info_file, 'r') as f:
            midi_info = json.load(f)

        # Convert the MIDI info into a more usable format, if necessary
        # For example, creating a dictionary that maps MIDI note numbers to note symbols
        note_symbols = {int(note["MIDI Note Number"]): note["Note Symbol"] for note in midi_info}
        return note_symbols

    def _parse_header(self, rows):
        """Parse the header to extract MIDI file metadata."""

        for row in rows:
            row = [field.strip() for field in row]

            # Identify the row type and extract relevant information
            if row[2] == 'note_on_c':
                # Stop metadata extraction when note rows are reached
                break
            if row[2] == 'Header':
                self.division = int(row[5])
            if row[2] == 'Tempo':
                self.tempo = int(row[3])
            if row[2] == 'Time_signature':
                self.notes_per_bar = int(row[3])

        # Validate extracted metadata
        if not all([self.division, self.tempo, self.notes_per_bar]):
            raise ValueError('Incomplete metadata, please check the MIDI CSV file')

        # Calculate pattern_length based on division and notes_per_bar
        self.pattern_length = self.division * self.notes_per_bar

        # Calculate BPM from the extracted tempo
        self.bpm = self._calculate_bpm(self.tempo)

    def _calculate_bpm(self, tempo):
        """Calculate beats per minute from tempo."""
        return self.MICROSECONDS_PER_MINUTE / tempo

    def establish_sections(self):
        """Establish the sections based on start times."""
        if not self.section_start_times or self.section_start_times[0] != 1:
            self.section_start_times = [1] + self.section_start_times

    def _process_row(self, row):
        """Processes a single row based on the event type."""
        row = [field.strip() for field in row]
        event_type = row[2]

        # Handle different MIDI event types by delegating to specific methods
        if event_type == 'Note_on_c':
            self._handle_note_on(row)
        elif event_type == 'Note_off_c':
            self._handle_note_off(row)
        elif event_type in ['Title_t', 'Instrument_name_t']:
            self._handle_instrument_declaration(row)

    def _handle_note_on(self, row):
        """Handles a 'Note_on_c' event."""
        time, track, note_value, velocity = self._extract_note_on_data(row)

        # Ensure the player and section are correctly identified
        current_player, current_section = self._get_player_and_section(track, time)

        # Calculate measure time and current measure
        measure_time = time % self.pattern_length
        current_measure = (time // self.pattern_length) + 1

        # Retrieve instrument and layout information
        instrument, layout, layout_name = self._get_instrument_and_layout(current_player)

        # Fetch x, y coordinates for the note
        x, y = self._get_note_coordinates(layout, note_value)

        # Create and add the new note
        note = self._create_note(time, measure_time, note_value, velocity, layout_name, x, y)
        self._add_note_to_pattern(note, current_player, current_measure, current_section)

    def _extract_note_on_data(self, row):
        """Extracts and returns data from a 'Note_on_c' event row."""
        time = int(row[1])
        track = int(row[0])
        note_value = int(row[4])
        velocity = int(row[5])
        return time, track, note_value, velocity

    def _get_player_and_section(self, track, time):
        """Determines the current player and section based on the track and time."""
        current_player = self.track_to_player.get(track, None)
        if current_player is None:
            raise ValueError(f"Track {track} is not assigned to any player.")

        # Determine the current section based on time and section_start_times
        current_section = 1
        for start_time in self.section_start_times:
            if time >= start_time:
                current_section += 1
            else:
                break

        return current_player, current_section

    def _get_instrument_and_layout(self, current_player):
        """Retrieve instrument and layout for the current player."""
        # Retrieve the instrument for the current player
        instrument_info = self.player_instruments.get(current_player, {})
        instrument = instrument_info.get("instrument", self.default_instrument)

        # Determine the layout file for the instrument
        layout_file = self.instrument_layout.get(instrument)
        if not layout_file:
            raise ValueError(f"No layout found for instrument: {instrument}")

        # Extract layout coordinates
        layout_coordinates = self.layout_coordinates.get(layout_file)
        if not layout_coordinates:
            raise ValueError(f"No layout coordinates found for layout file: {layout_file}")

        layout_name = layout_file.replace('_layout.json', '')

        return instrument, layout_coordinates, layout_name

    def _get_note_coordinates(self, layout_coordinates, note_value):
        """Retrieve x, y coordinates for the note based on its value and layout."""
        if note_value not in layout_coordinates:
            raise ValueError(f"No coordinates found for note value: {note_value} in the given layout.")

        # Assuming the layout_coordinates are stored as a list of coordinates for each note value,
        # and we're taking the first set of coordinates for simplicity.
        # You might need to adjust this if your data structure is different.
        coordinates = layout_coordinates[note_value][0]

        # Extract x and y values
        x = coordinates.get('x')
        y = coordinates.get('y')

        if x is None or y is None:
            raise ValueError(f"Incomplete coordinates for note value: {note_value} in the given layout.")

        return x, y

    def _create_note(self, time, measure_time, note_value, velocity, layout, x, y):
        """Creates and returns a new Note object."""
        note = Note(start_time=time, measure_time=measure_time, note_value=note_value,
                    velocity=velocity, note_name=self.note_symbols[note_value],
                    layout=layout, x=x, y=y)
        note.set_timing_info(self.bpm, self.division, self.fps)
        return note

    def _add_note_to_pattern(self, note, current_player, current_measure, current_section):
        """Adds a note to the appropriate pattern based on the player, measure, and section."""
        dict_key = (current_player, current_measure, current_section)

        # Check if there's an existing pattern for this combination of player, measure, and section
        for pattern_dict in self.unfinished_patterns:
            if dict_key in pattern_dict:
                pattern_dict[dict_key].add_note(note)
                return

        # If no existing pattern is found, create a new one
        new_pattern = Pattern(self.player_instruments[current_player]["instrument"])
        new_pattern.add_note(note)
        self.unfinished_patterns.append({dict_key: new_pattern})

    def _handle_note_off(self, row):
        """Handles a 'Note_off_c' event."""
        time, track, note_value = self._extract_note_off_data(row)

        current_player = self.track_to_player.get(track)
        if current_player is None:
            raise ValueError(f"Track {track} is not assigned to any player.")

        current_measure = (time // self.pattern_length) + 1

        # Find the corresponding 'Note_on_c' event and update the note's length
        self._update_note_length(note_value, time, current_player, current_measure)

    def _extract_note_off_data(self, row):
        """Extracts and returns data from a 'Note_off_c' event row."""
        time = int(row[1])
        track = int(row[0])
        note_value = int(row[4])
        return time, track, note_value

    def _update_note_length(self, note_value, time, current_player, current_measure):
        """Updates the length of a note based on the 'Note_off_c' event."""
        # Iterate through unfinished patterns to find the starting note
        for i, pattern_dict in enumerate(self.unfinished_patterns):
            for (player, measure, section), pattern in pattern_dict.items():
                if player == current_player and measure == current_measure:
                    # Find the corresponding starting note in this pattern
                    for note in pattern.notes:
                        if note.note_value == note_value and note.length is None:
                            # Update the note's length
                            note.length = time - note.start_time

                            # Check if completing this note finalizes the pattern
                            if pattern.is_complete():
                                # Prepare timing information tuple
                                timing_info = (self.bpm, self.division, self.fps, self.pattern_length)

                                # Finalize the pattern
                                pattern.finalize(self.player_measures, current_player, measure, section,
                                                 pattern.instrument, self.unfinished_patterns,
                                                 i, timing_info)
                            return

    def _process_unfinished_patterns(self, current_measure):
        """Processes and finalizes any patterns that are complete."""
        # Prepare timing information tuple
        timing_info = (self.bpm, self.division, self.fps, self.pattern_length)

        # Iterate through the list of unfinished patterns
        for i, pattern_dict in enumerate(self.unfinished_patterns[:]):
            for (current_player, measure_number, section_number), pattern in pattern_dict.items():
                if measure_number < current_measure and pattern.is_complete():
                    # Finalize the pattern
                    pattern.finalize(self.player_measures, current_player, measure_number,
                                     section_number, pattern.instrument, self.unfinished_patterns,
                                     i, timing_info)

                    # Remove the pattern from the list of unfinished patterns
                    del self.unfinished_patterns[i]
                    break  # Break to avoid modifying the list while iterating

    def _handle_instrument_declaration(self, row):
        """Handles instrument declarations in the MIDI file."""
        event_type, track, instrument_name = row[2], int(row[0]), row[3]

        # Assign a new player number to a new track if not already assigned
        if track not in self.track_to_player:
            self.track_to_player[track] = self.player_number
            self.player_number += 1

        # Get the current player number for this track
        current_player = self.track_to_player[track]

        # Process the instrument name and update the player's instrument
        instrument = self._process_instrument_name(instrument_name, event_type, current_player)
        self.player_instruments[current_player] = {"instrument": instrument, "layout": ""}

    def _process_instrument_name(self, instrument_name, event_type, current_player):
        """Processes and returns a standardized instrument name."""
        instrument_name = instrument_name.lower().replace('"', '')

        # If the event type is 'Title_t' or if this is the first declaration, use it as the instrument name
        if event_type == 'Title_t' or not self.player_instruments.get(current_player, {}).get("instrument"):
            return re.sub(r'\s+-?\d+$', '', instrument_name)

        # Otherwise, keep the existing instrument name
        return self.player_instruments[current_player]["instrument"]
