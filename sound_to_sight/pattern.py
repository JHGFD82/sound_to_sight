import mmh3


class Note:
    def __init__(self, measure_time, note_value, velocity, length):
        self.measure_time = measure_time
        self.note_value = note_value
        self.velocity = velocity
        self.length = length
        # Initialize X and Y with None, they can be updated later
        self.x = None
        self.y = None


class Pattern:
    def __init__(self, notes, player, instrument):
        self.players = [player]
        self.notes = notes  # notes is now a list of Note objects
        self.instrument = instrument
        self.pattern_hash = self.hash_pattern(notes)

    def hash_pattern(self, notes):
        pattern = [(note.measure_time, note.note_value, note.velocity, note.length) for note in notes]
        pattern_string = '_'.join('_'.join(map(str, tup)) for tup in pattern)
        return mmh3.hash(pattern_string)


def extract_patterns(df, notes_per_bar, division):
    patterns = []
    pattern_map = {}
    ticks_per_pattern = notes_per_bar * division
    unique_players = df['player'].unique()

    for start_time in range(0, df['time'].max(), ticks_per_pattern):
        end_time = start_time + ticks_per_pattern
        for player in unique_players:
            player_notes_df = df[(df['player'] == player) &
                                 (df['time'] >= start_time) &
                                 (df['time'] < end_time)]
            if player_notes_df.empty:
                continue

            note_objects = [Note(int(row['measure_time']), int(row['note']),
                                 int(row['velocity']), int(row['length']))
                            for _, row in player_notes_df.iterrows()]

            pattern = Pattern(note_objects, player, player_notes_df.iloc[0]['instrument'])
            existing_patterns = pattern_map.get(pattern.pattern_hash, [])

            for existing_pattern in existing_patterns:
                if all(existing_note.__dict__ == new_note.__dict__ for existing_note, new_note in zip(existing_pattern.notes, pattern.notes)) and existing_pattern.instrument == pattern.instrument:
                    if player not in existing_pattern.players:
                        existing_pattern.players.append(player)
                    break
            else:
                pattern_map.setdefault(pattern.pattern_hash, []).append(pattern)
                patterns.append(pattern)

    return patterns
