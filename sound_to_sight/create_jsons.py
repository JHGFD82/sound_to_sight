import json
import mmh3
import pandas as pd
from tqdm import tqdm


def convert_pattern_to_hashable(pattern_df):
    return list(
        zip(pattern_df['measure_time'].astype(int),
            pattern_df['note'].astype(int),
            pattern_df['velocity'].astype(int),
            pattern_df['length'].astype(int)))


def hash_pattern(pattern):
    pattern_string = "_".join(map(str, pattern))
    return mmh3.hash(pattern_string)


def identify_and_hash_patterns(df, notes_per_bar, division):
    patterns = {}
    pattern_details = []
    ticks_per_pattern = notes_per_bar * division
    unique_players = df['player'].unique()

    # Calculate total work for all players
    total_work = sum([(df[df['player'] == player]['time'].max() // ticks_per_pattern) for player in unique_players])

    # Initialize progress bar total_work
    progress_bar = tqdm(total=total_work, desc=f"Processing all {len(unique_players)} players",
                        colour='cyan', leave=False)

    for player in unique_players:
        df_player = df[df['player'] == player]
        max_time = df_player['time'].max()
        for start_tick in range(0, max_time, ticks_per_pattern):
            end_tick = start_tick + ticks_per_pattern
            pattern_df = df_player[(df_player['time'] >= start_tick) & (df_player['time'] < end_tick)]
            pattern = convert_pattern_to_hashable(pattern_df)
            pattern_hash = hash_pattern(pattern)
            if pattern_hash not in patterns:
                patterns[pattern_hash] = pattern
                pattern_details.append({
                    "pattern_hash": pattern_hash,
                    "notes": pattern
                })
            progress_bar.update(1)

    return patterns, pattern_details


def create_pattern_timing_json(df, patterns, notes_per_bar, division):
    pattern_timing_data = []
    ticks_per_pattern = notes_per_bar * division

    pattern_hashes = {hash_pattern(pattern): pattern for pattern in patterns.values()}
    unique_players = df['player'].unique()

    # Calculate total work for all players
    total_work = sum([(df[df['player'] == player]['time'].max() // ticks_per_pattern) for player in unique_players])

    # Initialize progress bar total_work
    progress_bar = tqdm(total=total_work, desc="Creating pattern timeline",
                        colour='blue', leave=False)

    for player in unique_players:
        df_player = df[df['player'] == player]

        max_time = df_player['time'].max()
        for start_tick in range(0, max_time, ticks_per_pattern):
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
            progress_bar.update(1)

    return {"pattern_timings": pattern_timing_data}


def create_player_hash_json(df, pattern_timing):
    player_hash_info = {}

    # Initialize tqdm progress bar
    total_timing_info = len(pattern_timing['pattern_timings'])
    progress_bar = tqdm(total=total_timing_info, desc="Assembling player information",
                        colour='magenta', leave=False)

    # Group by player and count hash repetitions
    for timing_info in pattern_timing['pattern_timings']:
        player = timing_info['player']
        pattern_hash = timing_info['pattern_hash']
        instrument = df[df['player'] == player]['instrument'].iloc[0]

        if player not in player_hash_info:
            player_hash_info[player] = {'instrument': instrument, 'hash_repetitions': {}, 'unique_hash_count': 0}

        if pattern_hash in player_hash_info[player]['hash_repetitions']:
            player_hash_info[player]['hash_repetitions'][pattern_hash]['count'] += 1
        else:
            player_hash_info[player]['hash_repetitions'][pattern_hash] = {'count': 1, 'position': (0, 0)}
            player_hash_info[player]['unique_hash_count'] += 1

        progress_bar.update(1)

    return player_hash_info


def create_jsons(df, notes_per_bar, division):
    patterns, pattern_details = identify_and_hash_patterns(df, notes_per_bar, division)
    pattern_timing = create_pattern_timing_json(df, patterns, notes_per_bar, division)
    player_hash_info = create_player_hash_json(df, pattern_timing)

    # Writing JSON files
    with open('pattern_details.json', 'w') as file:
        json.dump(pattern_details, file)
    with open('pattern_timing.json', 'w') as file:
        json.dump(pattern_timing, file)
    with open('player_hash_info.json', 'w') as file:
        json.dump(player_hash_info, file)

    return pattern_details, pattern_timing, player_hash_info
