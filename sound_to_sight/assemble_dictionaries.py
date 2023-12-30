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


def identify_and_hash_patterns(df, notes_per_bar, division, layouts, reversed_instruments):
    patterns = {}
    pattern_details_by_instrument_group = {}
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

            # define instrument_layout outside the if-else construct
            instrument_layout = reversed_instruments[df_player.iloc[0]['instrument']].replace('_layout.json', '')

            if pattern_hash not in patterns:
                patterns[pattern_hash] = pattern
                if instrument_layout not in pattern_details_by_instrument_group:
                    pattern_details_by_instrument_group[instrument_layout] = []
                pattern_details_by_instrument_group[instrument_layout].append({
                    "pattern_hash": pattern_hash,
                    "player": [player],
                    "notes": pattern
                })
            else:
                index = next((index for (index, d) in enumerate(pattern_details_by_instrument_group[instrument_layout])
                              if d["pattern_hash"] == pattern_hash), None)
                if player not in pattern_details_by_instrument_group[instrument_layout][index]['player']:
                    pattern_details_by_instrument_group[instrument_layout][index]['player'].append(player)
            progress_bar.update(1)

    return patterns, pattern_details_by_instrument_group


def create_pattern_timing_json(df, patterns, notes_per_bar, division):
    pattern_timing_data = {}
    ticks_per_pattern = notes_per_bar * division

    pattern_hashes = {hash_pattern(pattern): pattern for pattern in patterns.values()}
    unique_players = df['player'].unique()

    # Calculate total work for all players
    total_work = sum([(df[df['player'] == player]['time'].max() // ticks_per_pattern) for player in unique_players])

    # Initialize progress bar total_work
    progress_bar = tqdm(total=total_work, desc="Creating pattern timeline",
                        colour='blue', leave=False)

    for player in unique_players:
        pattern_timing_data[player] = []  # Initialize an empty list for each player
        df_player = df[df['player'] == player]

        max_time = df_player['time'].max()
        for start_tick in range(0, max_time, ticks_per_pattern):
            end_tick = start_tick + ticks_per_pattern
            pattern_df = df_player[(df_player['time'] >= start_tick) & (df_player['time'] < end_tick)]
            segment_pattern = convert_pattern_to_hashable(pattern_df)
            segment_hash = hash_pattern(segment_pattern)

            if segment_hash in pattern_hashes:
                pattern_timing_data[player].append({
                    "pattern_hash": segment_hash,
                    "start_time": start_tick
                })
            progress_bar.update(1)

    return pattern_timing_data


def create_player_hash_json(df, pattern_timing):
    player_hash_info = {}

    # Initialize tqdm progress bar
    total_timing_info = sum([len(v) for v in pattern_timing.values()])
    progress_bar = tqdm(total=total_timing_info, desc="Assembling player information",
                        colour='magenta', leave=False)

    # Group by player and count hash repetitions
    for player, player_pattern_timings in pattern_timing.items():
        instrument = df[df['player'] == player]['instrument'].iloc[0]
        player_hash_info[player] = {'instrument': instrument, 'hash_repetitions': {}, 'unique_hash_count': 0}
        for timing_info in player_pattern_timings:
            pattern_hash = timing_info['pattern_hash']
            if pattern_hash in player_hash_info[player]['hash_repetitions']:
                player_hash_info[player]['hash_repetitions'][pattern_hash] += 1
            else:
                player_hash_info[player]['hash_repetitions'][pattern_hash] = 1
                player_hash_info[player]['unique_hash_count'] += 1
            progress_bar.update(1)

    return player_hash_info


def create_jsons(df, notes_per_bar, division, layouts, reversed_instruments):
    patterns, pattern_details = identify_and_hash_patterns(df, notes_per_bar, division, layouts, reversed_instruments)
    pattern_timing = create_pattern_timing_json(df, patterns, notes_per_bar, division)
    player_hash_info = create_player_hash_json(df, pattern_timing)

    return pattern_details, pattern_timing, player_hash_info
