# SciSave - Serialization for Scientific Data

> * **Repository: [github.com/otvam/scisave](https://github.com/otvam/scisave)**
> * **PyPi: [pypi.org/project/scisave](https://pypi.org/project/scisave)**
> * **Conda: [anaconda.org/conda-forge/scisave](https://anaconda.org/conda-forge/scisave)**

## Summary

**SciSave** is a **Python serialization/deserialization** module:
* Specially targeted for **scientific applications**.
* Load **JSON/YAML configuration files**. 
* Load and write **JSON/Pickle data files**.
* Validate data with **JSON schemas**.

For **YAML files**, the following **custom extensions** are used:
*  Parse relative paths with respect to the YAML file (`!path`).
*  Include other YAML files into the YAML file (`!include`).
*  Evaluate a Python literal using literal_eval (`!eval`).
*  Substitute YAML strings with values from environment variables (`!env`).
*  Substitute YAML strings with values from a provided dictionary (`!sub`).
*  Merge a list of dicts (`!merge_dict`).
*  Merge a list of lists (`!merge_list`).

For **JSON files**, the following **custom extensions** are used:
* Allows the serialization/deserialization of complex numbers (`__complex__`).
* Allows the serialization/deserialization of NumPy arrays (`__numpy__`).
* Allows the serialization/deserialization as/from text and gzip files 

For **JSON schemas**, the following **custom extensions** are used:
* Handling NumPy types (integer, floating, and complex). 
* Handling NumPy multidimensional arrays.

The following **file extensions** are used:
* `.yaml, .yml` - for YAML files
* `.json, .js` - for JSON text files
* `.gz, .gzip` - for JSON gzip files
* `.pck, .pkl, .pickle` - for Pickle files

The JSON/YAML files with the custom extensions are still valid JSON/YAML files. 
Pickle is significantly faster than JSON for very large data files.

SciSave is written in Python (NumPy, PyYAML, and jsonschema are the only dependencies).
SciSave is respecting **semantic versioning** (starting from version 1.4).

## Warning

* Pickling data is not secure.
* Only load pickle files that you trust.

## Example

An example is located in the `example` folder of the repository:
* `run_data.py` contains an example file for the loader/dumper
* `config_main.yaml` YAML configuration file with custom extensions
* `config_include.yaml` YAML configuration file for include extension
* `config_schema.yaml` YAML file containing the JSON schema definition
* `dump.json` JSON text file for testing data dumping/loading
* `dump.gz` JSON gzip file for testing data dumping/loading
* `dump.pickle` Pickle file for testing data dumping/loading

## Project Links

* Repository: https://github.com/otvam/scisave
* Releases: https://github.com/otvam/scisave/releases
* Tags: https://github.com/otvam/scisave/tags
* Issues: https://github.com/otvam/scisave/issues
* PyPi: https://pypi.org/project/scisave
* Conda: https://anaconda.org/conda-forge/scisave

## Author

* **Thomas Guillod**
* Email: guillod@otvam.ch
* Website: https://otvam.ch

## Copyright

> (c) 2023 - Thomas Guillod
> 
>  BSD 2-Clause "Simplified" License
