import numpy as np
import json


def convert_numpy_to_python(data, numpy_type_conversions):
    if isinstance(data, tuple(numpy_type_conversions.keys())):
        return numpy_type_conversions[type(data)](data)
    elif isinstance(data, dict):
        return {
            convert_numpy_to_python(key, numpy_type_conversions): convert_numpy_to_python(value, numpy_type_conversions)
            for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_numpy_to_python(element, numpy_type_conversions) for element in data]
    else:
        return data


def export_jsons(data, filename):
    numpy_type_conversions = {np.int32: int, np.float32: float}  # Add more numpy types if needed
    data = convert_numpy_to_python(data, numpy_type_conversions)
    with open(filename + '.json', 'w') as file:
        json.dump(data, file, indent=4)
