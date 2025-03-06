"""
Module for validating data with JSON schemas (with extensions).
    - Handling NumPy types (integer, floating, and complex).
    - Handling NumPy multidimensional arrays.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "BSD License"

import numpy as np
import jsonschema


def _get_checker():
    """
    Create a schema type checker with the NumPy extensions.
    """

    def get_int(_, instance):
        return np.issubdtype(type(instance), np.integer)

    def get_float(_, instance):
        return np.issubdtype(type(instance), np.floating)

    def get_complex(_, instance):
        return np.iscomplexobj(instance)

    def get_array(_, instance):
        if isinstance(instance, np.ndarray):
            return jsonschema.Draft202012Validator.TYPE_CHECKER.is_type(instance.tolist(), "array")
        else:
            return jsonschema.Draft202012Validator.TYPE_CHECKER.is_type(instance, "array")

    # custom type checker
    type_checker = jsonschema.Draft202012Validator.TYPE_CHECKER
    type_checker = type_checker.redefine("number", get_float)
    type_checker = type_checker.redefine("complex", get_complex)
    type_checker = type_checker.redefine("integer", get_int)
    type_checker = type_checker.redefine("array", get_array)

    return type_checker


def _get_validator(extension):
    """
    Get a validator for JSON schemas.
    """

    if extension:
        schema_validator = jsonschema.validators.extend(
            jsonschema.Draft202012Validator,
            type_checker=_get_checker(),
        )
    else:
        schema_validator = jsonschema.Draft202012Validator

    return schema_validator


def validate_schema(data, schema, extension=True):
    """
    Validate data with a JSON schema (with/without custom extensions).
    """

    # get type checker
    schema_validator = _get_validator(extension)

    # validate schema
    schema_validator(schema).validate(data)
