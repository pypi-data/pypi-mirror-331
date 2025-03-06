"""
Module for deserialization of YAML files (with extensions).
    - Parse relative paths with respect to the YAML file (`!path`).
    - Include other YAML files into the YAML file (`!include`).
    - Evaluate a Python literal using literal_eval (`!eval`).
    - Substitute YAML strings with values from environment variables (`!env`).
    - Substitute YAML strings with values from a provided dictionary (`!sub`).
    - Merge a list of dicts (`!merge_dict`).
    - Merge a list of lists (`!merge_list`).
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "BSD License"

import ast
import os.path
import yaml


class _YamlLoader(yaml.SafeLoader):
    """
    This Python class offers extension to the YAML format.
        - parse relative paths (with respect to the YAML file)
        - include other YAML files (recursion possible)
        - evaluate a Python literal (using literal_eval)
        - substitute YAML strings with values from environment variables
        - substitute YAML strings with values from a provided dictionary
        - merge list of dicts
        - merge list of lists
    """

    def __init__(self, stream, include, substitute):
        """
        Constructor.
        Custom YAML loader subclassing the default loader.
        """

        # get the path of the YAML file for relative paths
        self.path_root = os.path.dirname(os.path.abspath(stream.name))

        # assign the substitution dictionary
        self.substitute = substitute

        # assign the list of included files
        self.include = include

        # flag indicating if any merge commands are used
        self.has_merge = False

        # call the constructor of the parent
        super().__init__(stream)

        # handling of YAML files inclusion
        def fct_handle_include(self, node):
            res = _YamlLoader._yaml_handling(self, node, self._extract_yaml)
            return res

        # handling of relative paths
        def fct_handle_path(self, node):
            res = _YamlLoader._yaml_handling(self, node, self._extract_path)
            return res

        # handling of string substitution from environment variables
        def fct_handle_env(self, node):
            res = _YamlLoader._yaml_handling(self, node, self._extract_env)
            return res

        # handling of string substitution from dictionary values
        def fct_handle_sub(self, node):
            res = _YamlLoader._yaml_handling(self, node, self._extract_sub)
            return res

        # handling of literal evaluation
        def fct_handle_eval(self, node):
            res = _YamlLoader._yaml_handling(self, node, self._extract_eval)
            return res

        # handling merge of a list of dicts
        def fct_handle_merge_dict(self, node):
            self.has_merge = True
            res = _YamlMerger(self.construct_sequence(node), "dict")
            return res

        # handling merge of a list of lists
        def fct_handle_merge_list(self, node):
            self.has_merge = True
            res = _YamlMerger(self.construct_sequence(node), "list")
            return res

        # add the extension to the YAML format
        _YamlLoader.add_constructor("!include", fct_handle_include)
        _YamlLoader.add_constructor("!path", fct_handle_path)
        _YamlLoader.add_constructor("!eval", fct_handle_eval)
        _YamlLoader.add_constructor("!env", fct_handle_env)
        _YamlLoader.add_constructor("!sub", fct_handle_sub)
        _YamlLoader.add_constructor("!merge_dict", fct_handle_merge_dict)
        _YamlLoader.add_constructor("!merge_list", fct_handle_merge_list)

    def _yaml_handling(self, node, fct):
        """
        Apply a function to a YAML node for list, dict, scalar.
        """

        if isinstance(node, yaml.ScalarNode):
            return fct(self.construct_scalar(node))
        elif isinstance(node, yaml.SequenceNode):
            result = []
            for arg in self.construct_sequence(node):
                result.append(fct(arg))
            return result
        elif isinstance(node, yaml.MappingNode):
            result = {}
            for tag, arg in self.construct_mapping(node).items():
                result[tag] = fct(arg)
            return result
        else:
            raise yaml.YAMLError("invalid YAML node type")

    def _extract_path(self, filename):
        """
        Find the path with respect to the YAML file path.
        """

        # check type
        if type(filename) is not str:
            raise yaml.YAMLError("path command arguments should be strings")

        # construct relative path
        filepath = os.path.join(self.path_root, filename)
        filepath = os.path.abspath(filepath)

        return filepath

    def _extract_yaml(self, filename):
        """
        Load an included YAML file.
        """

        # check type
        if type(filename) is not str:
            raise yaml.YAMLError("include command arguments should be strings")

        # construct relative path
        filepath = os.path.join(self.path_root, filename)
        filepath = os.path.abspath(filepath)

        # check for circular inclusion
        if filepath in self.include:
            raise yaml.YAMLError("include command cannot be circular")

        # update the list of included files
        include_tmp = self.include + [filepath]

        # load YAML file
        data = load_yaml(filepath, include_tmp, extension=True, substitute=self.substitute)

        return data

    def _extract_env(self, name):
        """
        Replace a string with a YAML data contained in an environment variable.
        """

        # check type
        if type(name) is not str:
            raise yaml.YAMLError("env command arguments should be strings")

        # get and check the variable
        value = os.getenv(name)
        if value is None:
            raise yaml.YAMLError("env variable is not existing: %s" % name)

        # load YAML string
        data = yaml.safe_load(value)

        return data

    def _extract_sub(self, name):
        """
        Replace a string with a Python data contained in a provided dictionary.
        """

        # check type
        if type(name) is not str:
            raise yaml.YAMLError("sub command arguments should be strings")

        # get and check the variable
        if self.substitute is None:
            raise yaml.YAMLError("sub dictionary is cannot be empty")

        # get and check the variable
        if name not in self.substitute:
            raise yaml.YAMLError("sub variable is not existing: %s" % name)

        # load YAML string
        data = self.substitute[name]

        return data

    def _extract_eval(self, var):
        """
        Evaluate a Python literal with the AST.
        """

        # check type
        if type(var) is not str:
            raise yaml.YAMLError("eval command arguments should be strings")

        # get and check the variable
        data = ast.literal_eval(var)

        return data


class _YamlMerger:
    """
    This Python class is used to merge YAML data.
        - a custom merge command is used with a list of arguments
        - the arguments (lists or dicts) are merged together
        - the merge is performed recursively

    The merge objects are created during the YAML parsing.
    The merge objects are replaced by the merged data after the parsing.
    """

    def __init__(self, data_list, data_type):
        """
        Constructor.
        Assign the list of data to be merged and the data type.
        """

        if type(data_list) is not list:
            raise yaml.YAMLError("arguments of the merge_dict / merge_list should be a list")

        self.data_list = data_list
        self.data_type = data_type

    def extract(self):
        """
        Merge a list of dicts or a list of lists.
        The merge is performed recursively.
        """

        if self.data_type == "dict":
            res = {}
            for data in self.data_list:
                data = _YamlMerger.merge(data)
                if type(data) is not dict:
                    raise yaml.YAMLError("merge_dict cannot only merge dictionaries")
                res.update(data)
        elif self.data_type == "list":
            res = []
            for data in self.data_list:
                data = _YamlMerger.merge(data)
                if type(data) is not list:
                    raise yaml.YAMLError("merge_list cannot only merge lists")
                res += data
        else:
            raise yaml.YAMLError("invalid merge type")

        return res

    @staticmethod
    def merge(data):
        """
        Walk through the data recursively and merge it.
        Find the merge objects and replace them with merged data.
        This function is used for the YAML merge extensions.
        """

        if type(data) is dict:
            for tag, val in data.items():
                data[tag] = _YamlMerger.merge(val)
        elif type(data) is list:
            for idx, val in enumerate(data):
                data[idx] = _YamlMerger.merge(val)
        elif type(data) is _YamlMerger:
            data = data.extract()
        else:
            pass

        return data


def load_yaml(filename, include, extension=True, substitute=None):
    """
    Load a YAML stream (with/without custom extensions).
    If required, merge the data (custom merge commands).
    """

    with open(filename) as fid:
        # create YAML loader (without or without extensions)
        if extension:
            loader = _YamlLoader(fid, include, substitute)
        else:
            loader = yaml.SafeLoader(fid)

        # parse, merge, and clean
        try:
            data = loader.get_single_data()
            if loader.has_merge:
                data = _YamlMerger.merge(data)
        finally:
            loader.dispose()

    return data
