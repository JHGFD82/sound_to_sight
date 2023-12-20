import json


def assign_instruments(dataframe):
    json_file_path = "midi_data/supported_instruments.json"
    # Load the JSON file
    with open(json_file_path) as json_file:
        data = json.load(json_file)

    # Create a new dictionary
    new_dict = {}

    # Iterate over the rows of the dataframe
    for i, row in dataframe.iterrows():
        # Get the corresponding key for each value in the 'instrument' column
        for key, value in data.items():
            if row['instrument'] in value:
                player_number = row['player']

                # Save the key as a value in the new dictionary, with the 'player' being the key
                new_dict[player_number] = key

    # Return the new dictionary
    return new_dict
