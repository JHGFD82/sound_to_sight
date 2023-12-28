import json
import mmh3
import pandas as pd
from tqdm import tqdm


def convert_pattern_to_hashable(pattern_df):
    return list(
        zip(pattern_df['note'].astype(int), pattern_df['velocity'].astype(int), pattern_df['length'].astype(int)))


def hash_pattern(pattern):
    pattern_string = "_".join(map(str, pattern))
    return mmh3.hash(pattern_string)


def identify_and_hash_patterns(df, notes_per_bar, division):
    patterns = {}
    pattern_details = []
    ticks_per_pattern = notes_per_bar * division

    players = df['player'].unique()
    players = [int(x) for x in players]
    for player in players:
        df_player = df[df['player'] == player]

        for start_tick in range(0, max(df_player['time']), ticks_per_pattern):
            end_tick = start_tick + ticks_per_pattern
            pattern_df = df_player[(df_player['time'] >= start_tick) & (df_player['time'] < end_tick)].copy()
            pattern_df[['note', 'velocity', 'length']] = pattern_df[['note', 'velocity', 'length']].astype(int)
            pattern = convert_pattern_to_hashable(pattern_df)
            pattern_hash = hash_pattern(pattern)

            pattern_key = (player, pattern_hash)  # Unique key for each player-pattern combination

            if pattern_key not in patterns:
                patterns[pattern_key] = pattern
                pattern_details.append({
                    "pattern_hash": pattern_hash,
                    "notes": pattern
                })

    return patterns, pattern_details


def create_pattern_timing_json(df, patterns, notes_per_bar, division):
    pattern_timing_data = []
    ticks_per_pattern = notes_per_bar * division

    players = df['player'].unique()
    for player in players:
        df_player = df[df['player'] == player]

        for pattern_hash, pattern in patterns.items():
            for start_tick in range(0, max(df_player['time']), ticks_per_pattern):
                end_tick = start_tick + ticks_per_pattern
                pattern_df = df_player[(df_player['time'] >= start_tick) & (df_player['time'] < end_tick)]

                if is_matching_pattern(pattern_df, pattern):
                    pattern_timing_data.append({
                        "pattern_hash": pattern_hash,
                        "start_time": int(start_tick),
                        "player": int(player)
                    })

    return {"pattern_timings": pattern_timing_data}


def is_matching_pattern(segment_df, pattern):
    segment_pattern = convert_pattern_to_hashable(segment_df)
    return hash_pattern(segment_pattern) == hash_pattern(pattern)


def create_jsons(df, notes_per_bar, division):
    patterns, pattern_details = identify_and_hash_patterns(df, notes_per_bar, division)
    pattern_timing_json = create_pattern_timing_json(df, patterns, notes_per_bar, division)

    # Writing JSON files
    with open('pattern_details.json', 'w') as file:
        json.dump(pattern_details, file)
    with open('pattern_timings.json', 'w') as file:
        json.dump(pattern_timing_json, file)
