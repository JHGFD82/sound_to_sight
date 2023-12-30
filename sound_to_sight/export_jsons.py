import numpy as np
import json


def export_jsons(dictionary, dictionary_name):
    def handle_np_int(data):
        if isinstance(data, np.int32):
            return int(data)
        elif isinstance(data, dict):
            return {handle_np_int(key): handle_np_int(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [handle_np_int(element) for element in data]
        else:
            return data

    dictionary = handle_np_int(dictionary)

    with open(dictionary_name + '.json', 'w') as file:
        json.dump(dictionary, file, indent=4)
