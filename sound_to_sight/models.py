import mmh3
from BPMtoFPS import ticks_to_seconds, seconds_to_frames


def ticks_to_frames(ticks, bpm, division, fps):
    return seconds_to_frames(ticks_to_seconds(ticks, bpm, division), fps)


class Note:
    def __init__(self, start_time, measure_time, note_value, velocity, note_name, layout, x, y):
        self.start_time = start_time
        self.measure_time = measure_time
        self.note_value = note_value
        self.velocity = velocity
        self.note_name = note_name
        self.layout = layout
        self.x = x
        self.y = y
        self._length = None
        self._bpm = None
        self._division = None
        self._fps = None

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, length):
        self._length = length
        self._update_frames()

    def set_timing_info(self, bpm, division, fps):
        self._bpm = bpm
        self._division = division
        self._fps = fps
        self._update_frames()

    def _update_frames(self):
        if self._bpm and self._division and self._fps:
            self.frame_start = ticks_to_frames(self.measure_time, self._bpm, self._division, self._fps)
            if self._length is not None:
                self.frame_duration = ticks_to_frames(self._length, self._bpm, self._division, self._fps)


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
        self._bpm = None
        self._division = None
        self._fps = None
        self._pattern_length = None
        self.frame_start = None

    def set_timing_info(self, bpm, division, fps, pattern_length):
        self._bpm = bpm
        self._division = division
        self._fps = fps
        self._pattern_length = pattern_length
        self._update_frame_start()

    def _update_frame_start(self):
        if all([self._bpm, self._division, self._fps, self._pattern_length]):
            self.frame_start = ticks_to_frames((self.measure_number - 1) * self._pattern_length, self._bpm, self._division, self._fps)
