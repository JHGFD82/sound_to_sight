import pandas as pd
import csv

MIDI_PLAYER_THRESHOLD = 1
player_data_mapping = {}
player_adjust = 0
DEFAULT_COLUMNS = ['header', 'time', 'status', 'num', 'note', 'velocity', 'extra1', 'extra2']


def import_midi(file_paths):
    def ensure_list(paths):
        if isinstance(paths, str):
            paths = paths.split()
        elif not isinstance(paths, list):
            raise ValueError("Input should be either a string or a list of file paths.")
        return paths

    def flatten_nested_data(nested_data):
        return [row for data_set in nested_data for row in data_set]

    def convert_to_midi_df(flat_data):
        return pd.DataFrame(flat_data, columns=DEFAULT_COLUMNS)

    def process_csv_row(row):
        # Extracting 'instrument_name_t' if present in the row
        if row[2] == ' Instrument_name_t':
            global player_adjust
            starting_player_number = int(row[0])
            player_number = starting_player_number + player_adjust
            instrument_name = row[3].strip().strip('"')  # Removing quotes
            player_data_mapping[str(starting_player_number)] = (player_number, instrument_name)
        return row

    def parse_and_adjust_csv(file_path):
        global player_adjust
        try:
            with open(file_path, newline='') as file:
                csv_reader = csv.reader(file)
                csv_data = list(csv_reader)
                player_adjust = -1 if int(csv_data[-2][0]) > MIDI_PLAYER_THRESHOLD else 0
        except FileNotFoundError:
            raise FileNotFoundError(f'Failed to open file "{file_path}".')
        return csv_data

    def create_processed_data(csv_data):
        return [process_csv_row(row) for row in csv_data]

    def process_csv_file(file_path):
        csv_data = parse_and_adjust_csv(file_path)
        processed_data = create_processed_data(csv_data)
        return processed_data

    file_paths = ensure_list(file_paths)
    csv_data_sets = [process_csv_file(path) for path in file_paths]
    csv_data_set_flat = flatten_nested_data(csv_data_sets)
    midi_df = convert_to_midi_df(csv_data_set_flat)

    # Add 'player' and 'instrument' columns to the DataFrame
    midi_df['player'] = pd.NA
    midi_df['instrument'] = pd.NA

    # Assigning instrument names to players in the DataFrame
    for original_player_number, (adjusted_player_number, instrument) in player_data_mapping.items():
        midi_df.loc[midi_df['header'] == original_player_number, 'player'] = adjusted_player_number
        midi_df.loc[midi_df['header'] == original_player_number, 'instrument'] = instrument

    return midi_df
