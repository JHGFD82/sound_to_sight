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
        self.section_start_times = section_start_times  # To manage different sections in the music

        # Initialize attributes to store MIDI file metadata
        self.division = None
        self.tempo = None
        self.notes_per_bar = None

        # Initialize current placement in row examination
        self.current_player = None
        self.current_measure = 1
        self.current_section = 0
        self.current_coords = None

        # Initialize data structures for parsing and processing
        self.player_measures = {}  # To store measures associated with each player
        self.unfinished_patterns = {}  # To keep track of unfinished musical patterns
        self.supported_instruments = {}  # To store information about supported instruments
        self.instrument_layout = {}  # To store layout information for each instrument
        self.layout_coordinates = {}  # To store coordinates for each instrument layout
        self.note_symbols = {}  # To map MIDI note numbers to symbols
        self.player_instruments = {}  # Maps player numbers to instruments
        self.track_to_player = {}  # Maps track numbers to player numbers
        self.player_number = 1  # Initial player number
        self.default_instrument = "keyboard"  # Default instrument in case of missing data
        self.pattern_length = None  # Initialize pattern_length

    def _load_from_json(self, file):
        with open(file, 'r') as f:
            return json.load(f)

    def _load_from_csv(self, file):
        with open(file, 'r') as f:
            return list(csv.reader(f))

    def _integer_row_data(self, row, fields):
        return [int(row[field]) for field in fields]

    def _string_row_data(self, row, fields):
        return [row[field].strip() for field in fields]

    def parse(self):
        """
        Parse Method

        Open and read the CSV file specified by `filename`. Then, perform further parsing operations on the contents of the file.

        Parameters:
        - self: The instance of the class calling the method.

        Raises:
        - N/A

        Returns:
        - `player_measures`: The final result after parsing.
        """
        # Open and read the CSV file
        rows = self._load_from_csv(self.filename)

        # Parse the header to extract MIDI file metadata
        self._parse_header(rows)

        # Validate section start time input
        self.establish_sections()

        # Load additional resources necessary for parsing
        self.supported_instruments = {}
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
        supported_instruments_json = 'midi_data/supported_instruments.json'
        self.supported_instruments = self._load_from_json(supported_instruments_json)

        # Populate the instrument_layout and layout_coordinates dictionaries
        for layout_file, instruments in self.supported_instruments.items():
            # Map each instrument to its corresponding layout file
            for instrument in instruments:
                self.instrument_layout[instrument] = layout_file

            # Load layout coordinates from the layout file
            layout_dir = 'midi_data/visual_layouts/'
            layout = self._load_from_json(layout_dir + layout_file)
            layout_coord = {int(key): values for key, values in layout.items()}
            self.layout_coordinates[layout_file] = layout_coord

    def _load_midi_info(self):
        """Loads MIDI information from a JSON file."""
        midi_info_file = 'midi_data/midi_info.json'  # Path to the MIDI info JSON file
        midi_info = self._load_from_json(midi_info_file)

        # Convert the MIDI info into a more usable format, if necessary
        # For example, creating a dictionary that maps MIDI note numbers to note symbols
        note_symbols = {int(note["MIDI Note Number"]): note["Note Symbol"] for note in midi_info}
        return note_symbols

    def _parse_header(self, rows):
        """Parse the header to extract MIDI file metadata."""

        for row in rows:
            event_type = self._string_row_data(row, [2])[0]

            # Identify the row type and extract relevant information
            if event_type == 'note_on_c':
                # Stop metadata extraction when note rows are reached
                break
            if event_type == 'Header':
                self.division = self._integer_row_data(row, [5])[0]
            if event_type == 'Tempo':
                self.tempo = self._integer_row_data(row, [3])[0]
            if event_type == 'Time_signature':
                self.notes_per_bar = self._integer_row_data(row, [3])[0]

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
        time = self._integer_row_data(row, [1])[0]
        event_type = self._string_row_data(row, [2])[0]

        self.current_measure = (time // self.pattern_length) + 1

        # Handle different MIDI event types by delegating to specific methods
        if event_type == 'Note_on_c':
            self._handle_note_on(row)
        elif event_type == 'Note_off_c':
            self._handle_note_off(row)
        elif event_type in ['Title_t', 'Instrument_name_t']:
            self._handle_instrument_declaration(row)

    def _handle_note_on(self, row):
        """Handles a 'Note_on_c' event."""
        time, track, note_value, velocity = self._integer_row_data(row, [1, 0, 4, 5])

        # Calculate measure time and current measure
        measure_time = time % self.pattern_length

        # Update the current section count, if applicable
        self._get_section()

        # Retrieve instrument and layout information
        if not self.player_instruments[self.current_player]['layout']:
            self._get_instrument_and_layout()

        x, y = self._get_note_coordinates(note_value)
        layout_name = self.player_instruments[self.current_player]['layout'].replace('_layout.json', '')
        note = self._create_note(time, measure_time, note_value, velocity, layout_name, x, y)
        instrument = self.player_instruments[self.current_player]['instrument']

        # Directly add note to pattern, avoiding multiple dictionary lookups
        dict_key = (self.current_player, self.current_measure, self.current_section)
        self.unfinished_patterns.setdefault(dict_key, Pattern(instrument)).add_note(note)

    def _get_section(self):
        # Determine the current section based on time and section_start_times
        if self.current_section < len(self.section_start_times) and (
                self.current_measure >= self.section_start_times[self.current_section]):
            self.current_section += 1

    def _get_instrument_and_layout(self):
        """Retrieve instrument and layout for the current player."""
        # Retrieve the instrument for the current player
        instrument = self.player_instruments[self.current_player]['instrument']
        layout_file = self.player_instruments[self.current_player]['layout']

        # Determine the layout file for the instrument
        while not layout_file:
            layout_file = self.instrument_layout.get(instrument)

            if not layout_file:
                user_instrument = input(f"The instrument '{instrument}' does not have a corresponding layout. "
                                        "Please input the name of a physical instrument, or press Enter to "
                                        "use a default keyboard-based layout: ").lower().strip()

                if user_instrument:
                    instrument = user_instrument
                else:
                    instrument = self.default_instrument

        self.player_instruments[self.current_player]['layout'] = layout_file

        # Extract layout coordinates
        self.current_coords = self.layout_coordinates.get(layout_file)
        if not self.current_coords:
            raise ValueError(f"No layout coordinates found for layout file: {layout_file}")

    def _get_note_coordinates(self, note_value):
        """Retrieve x, y coordinates for the note based on its value and layout."""
        if note_value not in self.current_coords:
            raise ValueError(f"No coordinates found for note value: {note_value} in the given layout.")

        # Assuming the layout_coordinates are stored as a list of coordinates for each note value,
        # and we're taking the first set of coordinates for simplicity.
        # You might need to adjust this if your data structure is different.
        coordinates = self.current_coords[note_value][0]

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

    def _handle_note_off(self, row):
        """Handles a 'Note_off_c' event."""
        time, track, note_value = self._integer_row_data(row, [1, 0, 4])

        # Process incomplete patterns more efficiently
        for pattern in self.unfinished_patterns.values():
            for note in pattern.notes:
                if note.note_value == note_value and note.length is None:
                    note.length = time - note.start_time
                    break

        # Finalize patterns if necessary, avoiding modifying the dict during iteration
        self._finalize_patterns()

    def _finalize_patterns(self):
        """Finalize patterns that are complete."""
        timing_info = (self.bpm, self.division, self.fps, self.pattern_length)

        # Create a list to track patterns to be finalized to avoid modifying the dictionary during iteration
        patterns_to_finalize = []
        for key, pattern in self.unfinished_patterns.items():
            _, measure_number, _ = key
            if measure_number < self.current_measure and pattern.is_complete():
                patterns_to_finalize.append((key, pattern))

        # Finalize the patterns outside the loop
        for key, pattern in patterns_to_finalize:
            player, measure, section = key
            pattern.finalize(self.player_measures, player, measure, section, pattern.instrument,
                             self.unfinished_patterns, key, timing_info)

    def _handle_instrument_declaration(self, row):
        """Handles instrument declarations in the MIDI file."""
        time, track = self._integer_row_data(row, [1, 0])
        event_type, instrument_name = self._string_row_data(row, [2, 3])

        # A new player means sections reset to 1
        self.current_section = 1

        # Assign a new player number to a new track if not already assigned
        if track not in self.track_to_player:
            self.track_to_player[track] = self.player_number
            self.player_number += 1

        # Get the current player number for this track
        self.current_player = self.track_to_player[track]

        # Process the instrument name and update the player's instrument
        instrument = self._process_instrument_name(instrument_name, event_type, self.current_player)
        self.player_instruments[self.current_player] = {"instrument": instrument, "layout": ""}

    def _process_instrument_name(self, instrument_name, event_type, current_player):
        """Processes and returns a standardized instrument name."""
        instrument_name = instrument_name.lower().replace('"', '')

        # If the event type is 'Title_t' or if this is the first declaration, use it as the instrument name
        if event_type == 'Title_t' or not self.player_instruments.get(current_player, {}).get("instrument"):
            return re.sub(r'\s+-?\d+$', '', instrument_name)

        # Otherwise, keep the existing instrument name
        return self.player_instruments[current_player]["instrument"]
