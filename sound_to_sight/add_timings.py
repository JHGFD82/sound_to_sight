from BPMtoFPS import ticks_to_seconds, seconds_to_timecode, seconds_to_frames


def add_timings(df, division, bpm, fps):
    seconds = df['time'].apply(lambda x: ticks_to_seconds(x, bpm, division))
    df['frames'] = seconds.apply(lambda x: seconds_to_frames(x, fps))
    df['timecode'] = seconds.apply(lambda x: seconds_to_timecode(x, fps))
    return df
