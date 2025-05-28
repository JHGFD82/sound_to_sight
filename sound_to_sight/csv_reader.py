import json
import csv
import re
from sound_to_sight import Note, Pattern


# Initialize current placement in row examination
class Status:
    """
    Status Class

    This class is used to keep track of the current state of the MIDI parsing process.
    It includes information about the current player, measure, section, and coordinates.

    Attributes:
        current_player (int): The current player number being processed.
        current_measure (int): The current measure number being processed.
        current_section (int): The current section number being processed.
        current_coords (tuple): The current coordinates of the note being processed.

    Methods:
        __init__: Initializes the Status object with default values.

    Returns:
        None
    """
    def __init__(self):
        self.current_player = None
        self.current_measure = 1
        self.current_section = 0
        self.current_coords = None

class MidiCsvParser:
    """
    MidiCsvParser Class
    
    This class is responsible for parsing MIDI CSV files and extracting relevant information such as
    note events, instrument declarations, and tempo information. It also manages the organization of
    musical patterns and their associated players.
    """

    # Constants for time calculations
    MICROSECONDS_PER_MINUTE = 60000000

    def __init__(self, filename: str, fps: int, section_start_times: list[int]):
    
        self.filename = filename
        self.fps = fps
        self.section_start_times = section_start_times  # To manage different sections in the music

        # Initialize attributes to store MIDI file metadata
        self.division = None
        self.tempo = None
        self.notes_per_bar = None

        # Initialize data structures for parsing and processing
        self.player_measures = {}  # To store measures associated with each player
        self.unfinished_patterns = {}  # To keep track of unfinished musical patterns
        self.supported_instruments = self._load_file('midi_data/supported_instruments.json')  # To store information about supported instruments
        self.instrument_layout = {}  # To store layout information for each instrument
        self.layout_coordinates = {}  # To store coordinates for each instrument layout
        self.note_symbols = self._load_midi_info()  # To map MIDI note numbers to symbols
        self.player_instruments = {}  # Maps player numbers to instruments
        self.track_to_player = {}  # Maps track numbers to player numbers
        self.player_number = 1  # Initial player number
        self.default_instrument = "keyboard"  # Default instrument in case of missing data
        self.pattern_length = None  # Initialize pattern_length
        self.total_length = 0

    def _load_file(self, file: str, filetype: str = "json") -> list[list[str]] | dict[str, str]:
        """
        Load and return data from a JSON or CSV file.

        Arguments:
            file (str): Path to the file.
            filetype (str): "json" or "csv".

        Returns:
            object: Parsed data (dict for JSON, list for CSV).
        """
        with open(file, 'r') as f:
            if filetype == "json":
                return json.load(f)
            elif filetype == "csv":
                return list(csv.reader(f))
            else:
                raise ValueError("Unsupported filetype: must be 'json' or 'csv'")

    from typing import Callable, Any

    def _row_data(self, row: list[str], fields: list[int], cast_func: Callable[[str], Any]) -> list[Any]:
        """
        Extracts data from a row based on specified fields and applies a casting function to each field.
        This method is used to convert the data in the specified fields to the desired type.
        
        Parameters:
            row (list): The row from which to extract data.
            fields (list): A list of field indices to extract from the row.
            cast_func (Callable[[str], Any]): A function to cast the extracted data to the desired type.

        Returns:
            list: A list of extracted and casted data.
        """
        # Extract data from the row based on specified fields and apply casting function
        return [cast_func(row[field]) for field in fields]

    def parse(self) -> tuple[dict[int, dict[int, dict[int, Pattern]]], list[int], float, int, int, int]:
        """
        Parse Method

        Open and read the CSV file specified by `filename`. Then, perform further parsing operations on the contents
        of the file.

        Parameters:
        - self: The instance of the class calling the method.

        Returns:
        - `player_measures`: The final result after parsing.
        """
        # Open and read the CSV file
        rows = self._load_file(self.filename)

        # Parse the header to extract MIDI file metadata
        self._parse_header(rows)

        # Validate section start time input
        self.establish_sections()

        # Load additional resources necessary for parsing
        self.supported_instruments = {}
        self._initialize_instrument_layouts()

        # Main loop to process each row in the CSV file
        for row in rows:
            self._process_row(row)

        # Return the final result after parsing
        return (self.player_measures, self.section_start_times, self.bpm, self.notes_per_bar,
                self.division, self.total_length)

    def _initialize_instrument_layouts(self):
        """
        Initialize instrument layouts and coordinates from JSON files.
        This method loads the supported instruments and their corresponding layouts from JSON files.
        It also creates a dictionary to store already loaded layouts to prevent duplicate loading.
        
        Returns:
            None
        """
        # Create a dictionary to store already loaded layouts to prevent duplicate loading
        loaded_layouts = {}

        # Populate the instrument_layout and layout_coordinates dictionaries
        for instrument, data in self.supported_instruments.items():
            layout_file = data['layout']

            # Check if layout is already loaded
            if layout_file not in loaded_layouts:
                layout_dir = 'midi_data/visual_layouts/'
                layout = self._load_file(layout_dir + layout_file)
                layout_coord = {int(key): values for key, values in layout.items()}
                loaded_layouts[layout_file] = layout_coord

            # Assign loaded layout to the instrument
            self.instrument_layout[instrument] = layout_file
            self.layout_coordinates[instrument] = loaded_layouts[layout_file]

    def _load_midi_info(self) -> dict[int, str]:
        """
        Load MIDI info from a JSON file and convert it into a more usable format.
        This method reads the MIDI info JSON file and creates a dictionary that maps MIDI note numbers to note symbols.
        It is assumed that the JSON file contains a list of dictionaries with "MIDI Note Number" and "Note Symbol" keys.

        Returns:
            dict[int, str]: A dictionary mapping MIDI note numbers to note symbols.
        """
        # Load MIDI info from the JSON file
        midi_info_file = 'midi_data/midi_info.json'  # Path to the MIDI info JSON file
        midi_info = self._load_file(midi_info_file)

        # Convert the MIDI info into a more usable format, if necessary
        # For example, creating a dictionary that maps MIDI note numbers to note symbols
        note_symbols = {int(note["MIDI Note Number"]): note["Note Symbol"] for note in midi_info}
        return note_symbols

    def _parse_header(self, rows: list[list[str]]):
        """
        Parse the header of the MIDI CSV file to extract metadata such as division, tempo, and notes per bar.
        This method iterates through the rows of the CSV file and identifies the relevant metadata based on the event type.
        It stops parsing when it encounters a 'note_on_c' event, as this indicates the start of the actual note events.
        It also validates the extracted metadata to ensure that all required fields are present.
        If any required metadata is missing, it raises a ValueError to indicate the issue.

        Parameters:
            rows (list): A list of rows from the MIDI CSV file.
        
        Raises:
            ValueError: If any required metadata is missing or incomplete.

        Returns:
            None
        """
        # Initialize metadata attributes
        for row in rows:
            event_type = self._row_data(row, [2], lambda x: x.strip())[0]

            # Identify the row type and extract relevant information
            if event_type == 'note_on_c':
                # Stop metadata extraction when note rows are reached
                break
            if event_type == 'Header':
                self.division = self._row_data(row, [5], int)[0]
            if event_type == 'Tempo':
                self.tempo = self._row_data(row, [3], int)[0]
            if event_type == 'Time_signature':
                self.notes_per_bar = self._row_data(row, [3], int)[0]

        # Validate extracted metadata
        if not all([self.division, self.tempo, self.notes_per_bar]):
            raise ValueError('Incomplete metadata, please check the MIDI CSV file')

        # Calculate pattern_length based on division and notes_per_bar
        self.pattern_length = self.division * self.notes_per_bar

        # Calculate BPM from the extracted tempo
        self.bpm = self._calculate_bpm(self.tempo)

    def _calculate_bpm(self, tempo) -> float:
        """
        Calculate BPM from the given tempo in microseconds per quarter note.
        This method converts the tempo to BPM using the formula:
        BPM = (60 * 1,000,000) / tempo
        where tempo is the duration of a quarter note in microseconds.

        Parameters:
            tempo (int): The tempo in microseconds per quarter note.

        Raises:
            ValueError: If the tempo is not a positive integer or exceeds the maximum allowed value.
        
        Returns:
            float: The calculated BPM (Beats Per Minute).
        """
        # Calculate BPM from the given tempo
        if tempo <= 0:
            raise ValueError("Tempo must be a positive integer.")
        if tempo > self.MICROSECONDS_PER_MINUTE:
            raise ValueError("Tempo must be less than or equal to 60,000,000 microseconds.")
        # Calculate BPM using the formula
        # BPM = (60 * 1,000,000) / tempo
        # where tempo is the duration of a quarter note in microseconds
        return self.MICROSECONDS_PER_MINUTE / tempo

    def establish_sections(self):
        """
        Establish sections based on the provided section start times.
        This method checks if the section start times are provided and ensures that the first section starts at time 1.
        If the first section start time is not 1, it prepends 1 to the list of section start times.
        It also ensures that the section start times are in ascending order.
        
        Returns:
            None
        """
        # Ensure section start times are in ascending order
        self.section_start_times.sort()
        if not self.section_start_times:
            self.section_start_times = [1]
        elif len(self.section_start_times) == 1:
            self.section_start_times = [1, self.section_start_times[0]]
        elif len(self.section_start_times) > 1 and self.section_start_times[0] != 1:
            self.section_start_times = [1] + self.section_start_times

    def _process_row(self, row):
        """
        Process a single row of the MIDI CSV file.
        This method extracts relevant information from the row, such as time, event type, and instrument declarations.
        It updates the current measure and section based on the time information and handles different MIDI event types
        accordingly. It also manages the unfinished patterns and finalizes them when necessary.
        
        Parameters:
            row (list): A single row from the MIDI CSV file.
            
        Returns:
            None
        """
        # Extract relevant information from the row
        time = self._row_data(row, [1], int)[0]
        event_type = self._row_data(row, [2], lambda x: x.strip())[0]

        # Update the current measure based on the time and pattern length
        Status.current_measure = (time // self.pattern_length) + 1

        # Handle different MIDI event types by delegating to specific methods
        if event_type == 'Note_on_c':
            self._handle_note_on(row)
        elif event_type == 'Note_off_c':
            self._handle_note_off(row)
        elif event_type in ['Title_t', 'Instrument_name_t']:
            self._handle_instrument_declaration(row)
        elif event_type == 'End_track':
            self._find_total_length(row)

    def _find_total_length(self, row):
        """
        Finds the total length of the MIDI file based on the 'End_track' event.
        This method extracts the length from the row and updates the total length if it is greater than the current total length.
        
        Parameters:
            row (list): A single row from the MIDI CSV file.
            
        Returns:
            None
        """
        # Extract the length from the row and update the total length
        length = int(row[1])
        if length > self.total_length:
            self.total_length = length

    def _handle_note_on(self, row):
        """
        Handles a 'Note_on_c' event.
        This method extracts relevant information from the row, such as time, track, note value, and velocity.
        It calculates the measure time and current measure, updates the current section count if applicable,
        and retrieves instrument and layout information. It then creates a Note object and adds it to the unfinished patterns.
        
        Parameters:
            row (list): A single row from the MIDI CSV file.

        Returns:
            None
        """
        # Extract relevant information from the row
        time, track, note_value, velocity = self._row_data(row, [1, 0, 4, 5], int)

        # Calculate measure time and current measure
        measure_time = time % self.pattern_length

        # Update the current section count, if applicable
        self._get_section()

        # Retrieve instrument and layout information
        if not self.player_instruments[Status.current_player]['layout']:
            self._get_instrument_and_layout()

        x, y = self._get_note_coordinates(note_value)
        layout_name = self.player_instruments[Status.current_player]['layout'].replace('_layout.json', '')
        note = self._create_note(time, measure_time, note_value, velocity, layout_name, x, y)
        instrument = self.player_instruments[Status.current_player]['instrument']
        footage = self.player_instruments[Status.current_player]['footage']

        # Directly add note to pattern, avoiding multiple dictionary lookups
        dict_key = (Status.current_player, Status.current_measure, Status.current_section)
        self.unfinished_patterns.setdefault(dict_key, Pattern(instrument, footage)).add_note(note)

    def _get_section(self):
        """
        Update the current section based on the time and section start times.
        This method checks if the current measure is greater than or equal to the start time of the current section.
        If so, it increments the current section count. This is used to manage different sections in the music.
        
        Returns:
            None
        """
        # Determine the current section based on time and section_start_times
        if Status.current_section < len(self.section_start_times) and (
                Status.current_measure >= self.section_start_times[Status.current_section]):
            Status.current_section += 1

    def _get_instrument_and_layout(self):
        """Retrieve instrument and layout for the current player.
        This method checks if the current player has a layout defined. If not, it prompts the user to input an instrument name.
        It also retrieves the layout file and footage information for the instrument.
        If the layout file is not found, it prompts the user to input a physical instrument name or use a default keyboard-based layout.
        
        Returns:
            None
        """
        # Retrieve the instrument for the current player
        instrument = self.player_instruments[Status.current_player]['instrument']
        layout_file = self.player_instruments[Status.current_player]['layout']

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

        self.player_instruments[Status.current_player]['layout'] = layout_file
        self.player_instruments[Status.current_player]['footage'] = self.supported_instruments[instrument]['footage']

        # Extract layout coordinates
        Status.current_coords = self.layout_coordinates.get(instrument)
        if not Status.current_coords:
            raise ValueError(f"No layout coordinates found for layout file: {layout_file}")

    def _get_note_coordinates(self, note_value) -> tuple[int, int]:
        """Retrieve x, y coordinates for the note based on its value and layout.
        This method checks if the note value exists in the current layout coordinates.
        If it does, it retrieves the x and y coordinates. If not, it raises a ValueError.
        
        Parameters:
            note_value (int): The MIDI note value for which to retrieve coordinates.
        
        Raises:
            ValueError: If the note value is not found in the current layout coordinates.
            
        Returns:
            tuple[int, int]: A tuple containing the x and y coordinates for the note.
        """
        # Check if the note value exists in the current layout coordinates
        if note_value not in Status.current_coords:
            raise ValueError(f"No coordinates found for note value: {note_value} in the given layout.")

        # Assuming the layout_coordinates are stored as a list of coordinates for each note value,
        # and we're taking the first set of coordinates for simplicity.
        # You might need to adjust this if your data structure is different.
        coordinates = Status.current_coords[note_value][0]

        # Extract x and y values
        x = coordinates.get('x')
        y = coordinates.get('y')

        if x is None or y is None:
            raise ValueError(f"Incomplete coordinates for note value: {note_value} in the given layout.")

        return x, y

    def _create_note(self, time, measure_time, note_value, velocity, layout, x, y) -> Note:
        """Creates and returns a new Note object.
        This method initializes a Note object with the provided parameters and sets its timing information.
        
        Parameters:
            time (int): The time at which the note starts.
            measure_time (int): The time within the measure.
            note_value (int): The MIDI note value.
            velocity (int): The velocity of the note.
            layout (str): The layout name for the note.
            x (int): The x coordinate for the note.
            y (int): The y coordinate for the note.
            
        Returns:
            Note: A new Note object initialized with the provided parameters.
        """
        # Create a new Note object with the provided parameters
        note = Note(start_time=time, measure_time=measure_time, note_value=note_value,
                    velocity=velocity, note_name=self.note_symbols[note_value],
                    layout=layout, x=x, y=y)
        note.set_timing_info(self.bpm, self.division, self.fps)
        return note

    def _handle_note_off(self, row):
        """Handles a 'Note_off_c' event.
        This method extracts relevant information from the row, such as time, track, and note value.
        It updates the unfinished patterns by setting the length of the note to the difference between the current time
        and the start time of the note. It also finalizes patterns if necessary.
        
        Parameters:
            row (list): A single row from the MIDI CSV file.
        
        Returns:
            None
        """
        # Extract relevant information from the row
        time, track, note_value = self._row_data(row, [1, 0, 4], int)

        # Process incomplete patterns more efficiently
        for pattern in self.unfinished_patterns.values():
            for note in pattern.notes:
                if note.note_value == note_value and note.length is None:
                    note.length = time - note.start_time
                    break

        # Finalize patterns if necessary, avoiding modifying the dict during iteration
        self._finalize_patterns()

    def _finalize_patterns(self):
        """
        Finalize patterns that are complete.
        This method checks the unfinished patterns and finalizes them if they are complete.
        It also updates the player measures and timing information for the finalized patterns.
        This is done to avoid modifying the dictionary while iterating over it.
        
        Returns:
            None
        """
        # Update the player measures with the current measure
        timing_info = (self.bpm, self.division, self.fps, self.pattern_length)

        # Create a list to track patterns to be finalized to avoid modifying the dictionary during iteration
        patterns_to_finalize = []
        for key, pattern in self.unfinished_patterns.items():
            _, measure_number, _ = key
            if measure_number < Status.current_measure and pattern.is_complete():
                patterns_to_finalize.append((key, pattern))

        # Finalize the patterns outside the loop
        for key, pattern in patterns_to_finalize:
            player, measure, section = key
            pattern.finalize(self.player_measures, player, measure, section, pattern.instrument, pattern.footage,
                             self.unfinished_patterns, key, timing_info)

    def _handle_instrument_declaration(self, row):
        """Handles instrument declarations in the MIDI file."""
        _, track = self._row_data(row, [1, 0], int)
        event_type, instrument_name = self._row_data(row, [2, 3], lambda x: x.strip())

        # A new player means sections reset to 1
        Status.current_section = 1

        # Assign a new player number to a new track if not already assigned
        if track not in self.track_to_player:
            self.track_to_player[track] = self.player_number
            self.player_number += 1

        # Get the current player number for this track
        Status.current_player = self.track_to_player[track]

        # Process the instrument name and update the player's instrument
        instrument = self._process_instrument_name(instrument_name, event_type, Status.current_player)
        self.player_instruments[Status.current_player] = {"instrument": instrument, "layout": "", "footage": ""}

    def _process_instrument_name(self, instrument_name, event_type, current_player) -> str:
        """Processes and returns a standardized instrument name."""
        instrument_name = instrument_name.lower().replace('"', '')

        # If the event type is 'Title_t' or if this is the first declaration, use it as the instrument name
        if event_type == 'Title_t' or not self.player_instruments.get(current_player, {}).get("instrument"):
            return re.sub(r'\s+-?\d+$', '', instrument_name)

        # Otherwise, keep the existing instrument name
        return self.player_instruments[current_player]["instrument"]
