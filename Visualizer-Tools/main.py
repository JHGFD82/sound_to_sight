# main.py

from Visualizer-Tools import import_midi, clean_data, add_sections, note_lengths, generate_fake_notes, create_keyboard, keyboard_side, BPMtoFPS

def main():
    df = import_midi([
        'CSVs/Six Marimbas Track 1.csv', 
        'CSVs/Six Marimbas Track 2.csv', 
        'CSVs/Six Marimbas Track 3.csv', 
        'CSVs/Six Marimbas Track 4.csv', 
        'CSVs/Six Marimbas Track 5.csv', 
        'CSVs/Six Marimbas Track 6.csv'
    ])
    df = clean_data(df)
    df = add_sections(df, [1, 329, 676])
    df = note_lengths(df)
    fake_notes = list(generate_fake_notes())
    keyboard = create_keyboard(df, fake_notes)
    df = keyboard_side(df, keyboard)

if __name__ == "__main__":
    main()