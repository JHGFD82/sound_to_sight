import mmh3


class Note:
    def __init__(self, start_time, measure_time, note_value, velocity, note_name, layout, x, y, length=None):
        self.start_time = start_time
        self.measure_time = measure_time
        self.length = length
        self.note_value = note_value
        self.velocity = velocity
        self.note_name = note_name
        self.layout = layout
        # x and y will be initialized as None and can be updated later.
        self.x = x
        self.y = y


class Pattern:
    def __init__(self, instrument):
        self.notes = []
        self.instrument = instrument
        self.hash = None

    def add_note(self, note):
        self.notes.append(note)

    def calculate_hash(self, notes):
        pattern = [(note.measure_time, note.note_value, note.velocity, note.length, note.layout) for note in notes]
        pattern_string = '_'.join('_'.join(map(str, tup)) for tup in pattern)
        return mmh3.hash(pattern_string)


class PlayerMeasure:
    def __init__(self, measure_number, section_number, player_number, instrument, pattern):
        self.measure_number = measure_number
        self.section_number = section_number
        self.player_number = player_number
        self.instrument = instrument
        self.pattern = pattern
        self.play_count = 1
