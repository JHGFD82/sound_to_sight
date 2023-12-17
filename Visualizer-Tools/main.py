# main.py

import os
import argparse
from . import (import_midi, clean_data, add_sections, note_lengths, generate_fake_notes, create_keyboard,
               keyboard_side, BPMtoFPS)


def main(file_list):
    # Check that the files exist at the specified locations
    for file in file_list:
        if not os.path.isfile(file):
            raise FileNotFoundError(f"No file found at the specified location: {file}")
    df = import_midi(file_list)
    df, division = clean_data(df)
    df = add_sections(df, [1, 329, 676])
    df = note_lengths(df)
    fake_notes = list(generate_fake_notes())
    keyboard = create_keyboard(df, fake_notes)
    df = keyboard_side(df, keyboard)
    df = BPMtoFPS(df)
    df.to_csv('output.csv', index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some files.")
    parser.add_argument("files", nargs="+", help="List of files to process")
    args = parser.parse_args()

    main(args.files)
