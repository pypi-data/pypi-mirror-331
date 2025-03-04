import os 
import json
from typing import Dict, Any
import yaml  # pip install PyYAML

from feature_flags.v1.utilities.find_feature_yaml import find_feature_yaml

class UsingBasicFlatFileV1:

    def __init__(self, filepath=find_feature_yaml(), format="yaml"):

        # if not found, create it
        if not filepath:
            filepath = F"features.{format}"
            with open(filepath, 'w'): pass
            print(F"Created {os.path.abspath(filepath)}")

        # Initialization logic & processing
        filepath = os.path.abspath(filepath) 
        format = format.lower()
        format = "yaml" if ("yml" == format) else format
        format = "yaml" if ("yaml" == format) else "json"

        # Assigning final vars (in alphabetical order)
        self.filepath = filepath
        self.format = format

        if os.path.exists(filepath):
            return 

        # Creating initial blank file
        self._write_resources_to_file({})

    def _read_resources_from_file(self) -> Dict[Any, Any]:
        dictionary = {}
        format = self.format
        tries = 2
        i = 0
        while i < 2:
            try:
                with open(self.filepath, 'r') as file:
                    if "json" == self.format:
                        contents_string = file.read()
                        dictionary = json.loads(contents_string)
                    elif "yaml" == self.format:
                        dictionary = yaml.safe_load(file)
                return dictionary
            except Exception as e:
                format = "json" if "yaml" == format else "yaml"
                i += 1
                out_of_tries = i == tries
                if not out_of_tries:
                    continue
                raise Exception(e)
    
    def _write_resources_to_file(self, dictionary: Dict[Any, Any]):
        with open(self.filepath, 'w') as file:
            if "json" == self.format:
                json.dump(dictionary, file, indent=4)
            elif "yaml" == self.format:
                yaml.dump(dictionary, file, default_flow_style=False)