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

    for player in df['player'].unique():
        df_player = df[df['player'] == player]

        max_time = df_player['time'].max()
        for start_tick in range(0, max_time, ticks_per_pattern):
            end_tick = start_tick + ticks_per_pattern
            pattern_df = df_player[(df_player['time'] >= start_tick) & (df_player['time'] < end_tick)]
            pattern = convert_pattern_to_hashable(pattern_df)
            pattern_hash = hash_pattern(pattern)

            pattern_key = (int(player), pattern_hash)

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

    pattern_hashes = {hash_pattern(pattern): pattern for pattern in patterns.values()}

    for player in df['player'].unique():
        df_player = df[df['player'] == player]

        max_time = df_player['time'].max()
        for start_tick in tqdm(range(0, max_time, ticks_per_pattern)):
            end_tick = start_tick + ticks_per_pattern
            pattern_df = df_player[(df_player['time'] >= start_tick) & (df_player['time'] < end_tick)]
            segment_pattern = convert_pattern_to_hashable(pattern_df)
            segment_hash = hash_pattern(segment_pattern)

            if segment_hash in pattern_hashes:
                pattern_timing_data.append({
                    "pattern_hash": segment_hash,
                    "start_time": start_tick,
                    "player": int(player)
                })

    return {"pattern_timings": pattern_timing_data}


def create_jsons(df, notes_per_bar, division):
    patterns, pattern_details = identify_and_hash_patterns(df, notes_per_bar, division)
    pattern_timing_json = create_pattern_timing_json(df, patterns, notes_per_bar, division)

    # Writing JSON files
    with open('pattern_details.json', 'w') as file:
        json.dump(pattern_details, file)
    with open('pattern_timing_json.json', 'w') as file:
        json.dump(pattern_timing_json, file)
