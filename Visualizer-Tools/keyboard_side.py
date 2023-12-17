# keyboard_side


def keyboard_side(df, keyboard):
    # The keyboard dictionary can now be used as a reference for where notes are going to be placed on the After Effects
    # composition. The next step is to update the original dataframe with a "y" column.
    df['y'] = df['note'].map(keyboard)

    # Before finishing with the 'y' column, the 'side' column will identify which side of the marimba is being played,
    # in case that distinction is made visually in After Effects (adding more realism to the playing).
    df['side'] = (df['y'] % 2 == 1)

    return df
