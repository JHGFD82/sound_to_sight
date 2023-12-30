from BPMtoFPS import ticks_to_seconds, seconds_to_frames


def convert_timing(details, timing, division, bpm, fps):
    # Convert ticks to frames for the 'details' dictionary
    for instrument, instrument_patterns in details.items():
        for pattern in instrument_patterns:
            for i, note in enumerate(pattern['notes']):
                note = list(note)
                timing_ticks = note[0]  # Get the timing information
                duration_ticks = note[3]  # Get the duration information

                # Convert timing from ticks to frames
                timing_seconds = ticks_to_seconds(timing_ticks, bpm, division)
                note[0] = int(seconds_to_frames(timing_seconds, fps))  # Convert to int for JSON serialization

                # Convert duration from ticks to frames
                duration_seconds = ticks_to_seconds(duration_ticks, bpm, division)
                note[3] = int(seconds_to_frames(duration_seconds, fps))  # Convert to int for JSON serialization

                note = tuple(note)  # Convert back to tuple and replace the original note
                pattern['notes'][i] = note

    # Convert ticks to frames for the 'timing' dictionary
    for _, pattern_timing in timing.items():
        for i, data in enumerate(pattern_timing):
            start_time_ticks = data['start_time']  # Get the start_time information

            # Convert start_time from ticks to frames
            start_time_seconds = ticks_to_seconds(start_time_ticks, bpm, division)
            data['start_time'] = int(seconds_to_frames(start_time_seconds, fps))  # Convert to int for JSON serialization

            pattern_timing[i] = data

    return details, timing
