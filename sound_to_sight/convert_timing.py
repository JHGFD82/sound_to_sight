from BPMtoFPS import ticks_to_seconds, seconds_to_frames


def convert_ticks_to_frames(ticks, bpm, division, fps):
    # Converts ticks to frames
    seconds = ticks_to_seconds(ticks, bpm, division)
    return int(seconds_to_frames(seconds, fps))


def convert_timing(details, timing, division, bpm, fps):
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
    return details, timing
