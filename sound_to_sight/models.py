import mmh3
from typing import Optional, List, Dict, Tuple, Union, cast
from BPMtoFPS import convert_time  # type: ignore[import-untyped]


def ticks_to_frames(ticks: int, bpm: float, division: int, fps: int) -> int:
    """Convert MIDI ticks to video frames using BPM, division, and FPS parameters."""
    # BPMtoFPS expects bpm as int, so we'll convert it
    result = convert_time('ticks', 'frames', bpm=int(bpm), fps=float(fps), ticks_per_beat=division, input_value=ticks)  # type: ignore[misc]
    
    # Handle the return value which can be a dict or a single value
    if isinstance(result, dict) and 'frames' in result:
        frames_value = result['frames']  # type: ignore[misc]
        return int(cast(Union[int, float, str], frames_value))
    elif isinstance(result, (int, float)):
        return int(result)
    else:
        # Fallback calculation if the library doesn't work as expected
        # Formula: (ticks / division) * (bpm / 60) * fps
        beats = ticks / division
        seconds = beats * (60 / bpm)
        frames = seconds * fps
        return int(frames)


class Note:
    def __init__(self, start_time: int, measure_time: int, note_value: int, velocity: int, note_name: str, layout: str, x: float, y: float):
        self.start_time = start_time
        self.measure_time = measure_time
        self.note_value = note_value
        self.velocity = velocity
        self.note_name = note_name
        self.layout = layout
        self.x = x
        self.y = y
        self._length: Optional[int] = None
        self._bpm: Optional[float] = None
        self._division: Optional[int] = None
        self._fps: Optional[int] = None
        self.frame_start: Optional[int] = None
        self.frame_duration: Optional[int] = None

    @property
    def length(self) -> Optional[int]:
        return self._length

    @length.setter
    def length(self, length: Optional[int]) -> None:
        self._length = length
        self._update_frames()

    def set_timing_info(self, bpm: float, division: int, fps: int) -> None:
        self._bpm = bpm
        self._division = division
        self._fps = fps
        self._update_frames()

    def _update_frames(self) -> None:
        if self._bpm and self._division and self._fps:
            self.frame_start = ticks_to_frames(self.measure_time, self._bpm, self._division, self._fps)
            if self._length is not None:
                self.frame_duration = ticks_to_frames(self._length, self._bpm, self._division, self._fps)


class Pattern:
    def __init__(self, instrument: str, footage: str):
        self.notes: List[Note] = []
        self.instrument = instrument
        self.footage = footage
        self.hash: Optional[int] = None

    def add_note(self, note: Note) -> None:
        # You can add any checks or preprocessing here if needed
        self.notes.append(note)

    def calculate_hash(self) -> int:
        pattern = [(note.measure_time, note.note_value, note.velocity, note.length, note.layout) for note in self.notes]
        pattern_string = '_'.join('_'.join(map(str, tup)) for tup in pattern)
        return mmh3.hash(pattern_string)

    def is_complete(self) -> bool:
        """Check if all notes in the pattern are complete (have lengths)."""
        return all(note.length is not None for note in self.notes)

    def finalize(self, player_measures: Dict[int, Dict[int, Dict[int, 'Pattern']]], current_player: int, measure_number: int, 
                 section_number: int, instrument: str, footage: str, unfinished_patterns: Dict[Tuple[int, int, int], 'Pattern'], 
                 index: Tuple[int, int, int], timing_info: Tuple[float, int, int, int]) -> None:
        """Finalize the pattern and update relevant structures."""
        self.hash = self.calculate_hash()
        
        # Initialize player if not exists
        if current_player not in player_measures:
            player_measures[current_player] = {}
        
        # Initialize measure if not exists
        if measure_number not in player_measures[current_player]:
            player_measures[current_player][measure_number] = {}
        
        # Store the pattern
        player_measures[current_player][measure_number][section_number] = self

        del unfinished_patterns[index]


class PlayerMeasure:
    def __init__(self, measure_number: int, section_number: int, player_number: int, instrument: str, footage: str, pattern: Pattern):
        self.measure_number = measure_number
        self.section_number = section_number
        self.player_number = player_number
        self.instrument = instrument
        self.footage = footage
        self.pattern = pattern
        self.play_count = 1
        self._bpm: Optional[float] = None
        self._division: Optional[int] = None
        self._fps: Optional[int] = None
        self._pattern_length: Optional[int] = None
        self.frame_start: Optional[int] = None

    def set_timing_info(self, bpm: float, division: int, fps: int, pattern_length: int) -> None:
        self._bpm = bpm
        self._division = division
        self._fps = fps
        self._pattern_length = pattern_length
        self._update_frame_start()

    def _update_frame_start(self) -> None:
        if all([self._bpm, self._division, self._fps, self._pattern_length]):
            # Type assertions are safe here because we checked all values are not None above
            assert self._bpm is not None and self._division is not None and self._fps is not None and self._pattern_length is not None
            self.frame_start = ticks_to_frames((self.measure_number - 1) * self._pattern_length,
                                               self._bpm, self._division, self._fps)
