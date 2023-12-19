import pandas as pd
import csv

DEFAULT_PLAYER_ADJUSTMENT = 0
MIDI_PLAYER_THRESHOLD = 1
DEFAULT_COLUMNS = ['header', 'time', 'status', 'num', 'note', 'velocity', 'extra1', 'extra2', 'player']


def import_midi(file_paths):
    """
    Import MIDI files and convert them into a pandas DataFrame.

    Parameters:
    file_paths (str or list): Path(s) to the MIDI file(s) to be imported.

    Returns:
    pandas.DataFrame: MIDI data converted into a DataFrame.

    """

    def ensure_list(paths):
        if isinstance(paths, str):
            paths = paths.split()
        elif not isinstance(paths, list):
            raise ValueError(
                "Input should be either a string of a single file path, multiple file paths separated by spaces, "
                "or a list of file paths.")
        return paths

    def flatten_nested_data(nested_data):
        return [row for data_set in nested_data for row in data_set]

    def convert_to_midi_df(flat_data):
        return pd.DataFrame(flat_data, columns=DEFAULT_COLUMNS)

    def process_csv_row(row, player_adjust, max_cols):
        padding = [0] * (max_cols - len(row))
        return row + padding + [int(row[0]) + player_adjust]

    def parse_and_adjust_csv(file_path):
        player_adjust = DEFAULT_PLAYER_ADJUSTMENT
        try:
            with open(file_path, newline='') as file:
                csv_reader = csv.reader(file)
                csv_data = list(csv_reader)
                if int(csv_data[-2][0]) > MIDI_PLAYER_THRESHOLD:
                    player_adjust -= 1
                max_cols = max(len(row) for row in csv_data)
        except FileNotFoundError:
            raise FileNotFoundError(
                f'Failed to open file "{file_path}". Please ensure that the file exists and that you have entered the '
                f'correct file name.')
        return csv_data, player_adjust, max_cols

    def create_processed_data(csv_data, player_adjust, max_cols):
        return [process_csv_row(row, player_adjust, max_cols) for row in csv_data]

    def process_csv_file(file_path):
        csv_data, player_adjust, max_cols = parse_and_adjust_csv(file_path)
        processed_data = create_processed_data(csv_data, player_adjust, max_cols)
        return processed_data

    file_paths = ensure_list(file_paths)
    csv_data_sets = [process_csv_file(path) for path in file_paths]
    csv_data_set_flat = flatten_nested_data(csv_data_sets)
    midi_df = convert_to_midi_df(csv_data_set_flat)

    return midi_df
