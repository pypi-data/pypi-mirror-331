"""
Module for serialization and deserialization of JSON files (with extensions).
    - Allows the serialization/deserialization of complex numbers (`__complex__`).
    - Allows the serialization/deserialization of NumPy arrays (`__numpy__`).
    - Allows the serialization/deserialization as/from text and gzip files
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "BSD License"

import json
import gzip
import numpy as np


class _JsonNumPyEncoder(json.JSONEncoder):
    """
    This Python class offers extension to the JSON format (encoder).
        - encode NumPy scalar types
        - encode NumPy array types
    """

    def __init__(self, **kwargs):
        """
        Constructor
        """

        super().__init__(**kwargs)

    def default(self, obj):
        """
        Function encoding NumPy types as dictionaries.
        """

        # encode numpy scalars and arrays
        if np.isscalar(obj) and np.iscomplexobj(obj):
            return {
                "__complex__": None,
                "real": obj.real,
                "imag": obj.imag,
            }
        elif np.isscalar(obj) and np.issubdtype(obj.dtype, np.integer):
            return int(obj)
        elif np.isscalar(obj) and np.issubdtype(obj.dtype, np.floating):
            return float(obj)
        elif np.isscalar(obj) and np.issubdtype(obj.dtype, bool):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            # handle numpy array
            if np.iscomplexobj(obj):
                return {
                    "__numpy__": None,
                    "dtype": "complex",
                    "shape": obj.shape,
                    "data": {
                        "real": obj.real.flatten().tolist(),
                        "imag": obj.imag.flatten().tolist(),
                    },
                }
            elif np.issubdtype(obj.dtype, np.floating):
                return {
                    "__numpy__": None,
                    "dtype": "float",
                    "shape": obj.shape,
                    "data": obj.flatten().tolist(),
                }
            elif np.issubdtype(obj.dtype, np.integer):
                return {
                    "__numpy__": None,
                    "dtype": "int",
                    "shape": obj.shape,
                    "data": obj.flatten().tolist(),
                }
            elif np.issubdtype(obj.dtype, bool):
                return {
                    "__numpy__": None,
                    "dtype": "bool",
                    "shape": obj.shape,
                    "data": obj.flatten().tolist(),
                }
            else:
                TypeError("invalid numpy array for serialization")
        else:
            # if not numpy, default to the base encoder
            return json.JSONEncoder.default(self, obj)


class _JsonNumPyDecoder(json.JSONDecoder):
    """
    This Python class offers extension to the JSON format (decoder).
        - decode NumPy scalar types
        - decode NumPy array types
    """

    def __init__(self, **kwargs):
        """
        Constructor
        """

        kwargs.setdefault("object_hook", self.parse)
        super().__init__(**kwargs)

    def parse(self, obj):
        """
        Function decoding NumPy types from dictionaries.
        """

        # if not dict, do nothing
        if not isinstance(obj, dict):
            return obj

        # parse the extensions
        if "__complex__" in obj:
            # handling complex scalar
            real = obj["real"]
            imag = obj["imag"]
            return complex(real, imag)
        elif "__numpy__" in obj:
            # handle numpy array
            dtype = obj["dtype"]
            shape = obj["shape"]
            data = obj["data"]

            # parse the type
            if dtype == "complex":
                real = np.array(data["real"], dtype=complex).reshape(shape)
                imag = np.array(data["imag"], dtype=complex).reshape(shape)
                return real + 1j * imag
            elif dtype == "float":
                return np.array(data, dtype=float).reshape(shape)
            elif dtype == "int":
                return np.array(data, dtype=int).reshape(shape)
            elif dtype == "bool":
                return np.array(data, dtype=bool).reshape(shape)
        else:
            return obj


def load_json(filename, extension=True, compress=False):
    """
    Load a JSON file (with/without custom extensions).
    The JSON file can be a text file or a gzip file.
    """

    # create JSON decoder (without or without extensions)
    if extension:
        cls = _JsonNumPyDecoder
    else:
        cls = json.JSONDecoder

    # load the JSON data
    if compress:
        with gzip.open(filename, "rt", encoding="utf-8") as fid:
            data = json.load(fid, cls=cls)
    else:
        with open(filename) as fid:
            data = json.load(fid, cls=cls)

    return data


def write_json(filename, data, extension=True, compress=False):
    """
    Write a JSON file (with/without custom extensions).
    The JSON file can be a text file or a gzip file.
    """

    # create JSON encoder (without or without extensions)
    if extension:
        cls = _JsonNumPyEncoder
    else:
        cls = json.JSONEncoder

    # write the JSON data
    if compress:
        with gzip.open(filename, "wt", encoding="utf-8") as fid:
            json.dump(data, fid, cls=cls, indent=None)
    else:
        with open(filename, "w") as fid:
            json.dump(data, fid, cls=cls, indent=4)

    return data
