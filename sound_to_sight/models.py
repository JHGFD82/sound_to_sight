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

    def is_complete(self):
        """Check if all notes in the pattern are complete (have lengths)."""
        return all(note.length is not None for note in self.notes)

    def finalize(self, player_measures, current_player, measure_number, section_number,
                 instrument, unfinished_patterns, index):
        """Finalize the pattern and update relevant structures."""
        self.hash = self.calculate_hash(self.notes)
        if current_player not in player_measures:
            player_measures[current_player] = [PlayerMeasure(
                measure_number, section_number, current_player, instrument, self)]
        else:
            latest_pm = player_measures[current_player][-1]
            if not latest_pm.pattern.hash or self.hash != latest_pm.pattern.hash:
                player_measures[current_player].append(PlayerMeasure(
                    measure_number, section_number, current_player, instrument, self))
            else:
                latest_pm.play_count += 1
        del unfinished_patterns[index]


class PlayerMeasure:
    def __init__(self, measure_number, section_number, player_number, instrument, pattern):
        self.measure_number = measure_number
        self.section_number = section_number
        self.player_number = player_number
        self.instrument = instrument
        self.pattern = pattern
        self.play_count = 1
