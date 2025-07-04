import re
import json
import os
from typing import Optional
        

def load_data(file_path:str) -> Optional[dict]: 
    """
    loads and returns a dictionary from a JSON file if possible, else return False.
    """

    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=4)
        print(f"New file created at '{file_path}'")
        return {}
    
    # we try to read the file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return {}
    except Exception as e:
        print(f"An unexpected error occurred while reading '{file_path}': {e}")
        return False
    
    # we process the data into a dictionary.
    data = json.loads(content)
    if not isinstance(data, dict):
        print(f"Warning: '{file_path}' must be a dictionary, try changing the file path.")
    else:
        return data

def commit_data(file_path:str, data:dict):
    """
    write the given data to a JSON file.
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print('Data successfully committed')
        
    except Exception as e:
        print(f"Error writing to file '{file_path}': {e}, data could not be committed.")

def add(arg, data_dict):
    """
    Stages a new key-value pair in the data dictionary.
    """
    add_syntax = re.compile(r'^(?P<url>\S+)+\s+as\s+(?P<label>.+)')
    args = re.match(add_syntax, arg).groupdict()
    if not args:
        print('Invalid syntax for the add command')
        return
    new_key, new_value = args['label'], repr(args['url'])[1:-1]
    
    if new_key not in data_dict:
        data_dict[new_key] = new_value
        print(f"Key '{new_key}' with value '{new_value}' staged successfully.")
    else:
        print('key already used in staging')

def print_unstaged_data(arg, data):
    print(data)
    
def exit(arg=None,data=None):
    pass

def set_data_path(arg, data=None):
    path = arg
    save_point = load_data(path)

    data_path = arg
    staged_data = save_point.copy()
    commands['commit'] = lambda arg, data: commit_data(data_path, data)
    print(f'path setted at {path}')
    return save_point, data_path, staged_data

commands = {
    "add": add,
    "commit": commit_data,
    "print": print_unstaged_data,
    "exit": exit
}

command_syntax = re.compile(r'^\\(?P<command>\S+)\s*(?P<argument>.+)?')

