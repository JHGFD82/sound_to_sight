import numpy as np
import json
from typing import List, Union, Any, Dict


def convert_numpy_to_python(data: Union[dict, list, Any], numpy_type_conversions: Dict[type, type]) -> (
        Union)[Dict[Any, Any], List[Any], Any]:
    """
    Converts numpy data types to python data types based on provided type conversions dictionary.

    Args: data (dict, list, Any): The data to convert. It can be a dictionary, list, or any other data type.
    numpy_type_conversions (Dict[type, type]): A dictionary mapping numpy data types to their corresponding python
    data types.

    Returns:
        Union[Dict[Any, Any], List[Any], Any]: The converted data with numpy data types replaced by python data types.
    """
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


def export_jsons(data: dict, filename: str) -> None:
    """
    Exports the given data as JSON format to the specified file.

    Args:
        data (dict): The data to be exported as a JSON.
        filename (str): The name of the file to save the JSON data.

    Returns:
        None.
    """
    numpy_type_conversions = {np.int32: int, np.float32: float}  # Add more numpy types if needed
    data = convert_numpy_to_python(data, numpy_type_conversions)
    with open(filename + '.json', 'w') as file:
        json.dump(data, file, indent=4)
