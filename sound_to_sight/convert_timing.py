from BPMtoFPS import ticks_to_seconds, seconds_to_frames


def convert_ticks_to_frames(ticks, bpm, division, fps):
    # Converts ticks to frames
    seconds = ticks_to_seconds(ticks, bpm, division)
    return int(seconds_to_frames(seconds, fps))


def convert_timing(details, timing, timeline, division, bpm, fps):
    # Convert ticks to frames for the 'details' dictionary
    for instrument, instrument_patterns in details.items():
        for pattern in instrument_patterns:
            for i, note in enumerate(pattern['notes']):
                note = list(note)
                note[0] = convert_ticks_to_frames(note[0], bpm, division, fps)
                note[3] = convert_ticks_to_frames(note[3], bpm, division, fps)
                note = tuple(note)  # Convert back to tuple and replace the original note
                pattern['notes'][i] = note

    # Convert ticks to frames for the 'timing' dictionary
    for _, player_sections in timing.items():
        for _, pattern_timing in player_sections.items():
            for i, data in enumerate(pattern_timing):
                data['start_time'] = convert_ticks_to_frames(data['start_time'], bpm, division, fps)
                pattern_timing[i] = data

    # Convert ticks to frames for the 'timeline' dictionary
    for player, time_mapping in timeline.items():
        updated_mapping = {}  # Prepare a dictionary to hold updated values
        for start_time, pattern_hash in time_mapping.items():
            # Convert the start_time from ticks to frames
            converted_start_time = convert_ticks_to_frames(int(start_time), bpm, division, fps)
            # Update the mapping with the converted time
            updated_mapping[converted_start_time] = pattern_hash

        timeline[player] = updated_mapping  # Replace the original mapping with the updated one

    return details, timing, timeline
