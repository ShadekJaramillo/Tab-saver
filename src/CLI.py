import re
import json
from os.path import exists
import main

class session:
    def __init__(self, config):
        self.config = config
        self.folder = config['tab_folder']
        self.open_file = False
        self.urls = {}
        self.file_path = None
        self.open_file = None
        
    def open_group(self, file_name):
        path = app.folder + '/' + file_name
        urls = main.load_group_urls(path)
        if urls:
            self.urls = urls
            self.file_path = path
            self.open_file = file_name
            
    def new_group(self, file_name):
        if self.urls:
            self.file_path = app.folder + '/' + file_name
            self.open_file = file_name
        else:
            print('cant create file with no URLs')
    def info(self):
        info_dict = {
            "Opened file": app.open_file,
            "Folder": app.folder,
            "URLs": app.urls
        }
        return info_dict
        
    @property
    def run(self):
        return self._run
    @run.setter
    def run(self, value:bool):
        self._run = value
        

command_syntax = re.compile(
        r"^(?P<function>[a-zA-Z0-9]+)"  # Command name (at least one letter or number)
        r"(?:(?: +)-(?P<flags>[a-zA-Z0-9]+))?"  # Optional flags (space, '-', then letters/numbers)
        r"(?: +(?P<arguments>.*))?$"  # Optional arguments (space, then any characters until end of line)
    )

def open_group(args, flags, app:session):
    app.open_group(file_name = args)
    if app.urls:
        print(f'URLs successfully read from {args}')

def add(args, flags, app:session): # check syntax
    """
    stages a new URL to be saved later
    """
    add_syntax = re.compile(r'^(?P<url>\S+)+\s+as\s+(?P<label>.+)')
    args = re.match(add_syntax, args).groupdict()
    if not args:
        print('Invalid syntax for the add command')
        return
    new_key, new_value = args['label'], repr(args['url'])[1:-1]
    
    if new_key not in app.urls:
        app.urls[new_key] = new_value
        print(f"Key '{new_key}' with value '{new_value}' staged successfully.")
    else:
        print('key already staged')

def print_data(args, flags, app:session):
    print(app.info())

def save_to_file(args, flags, app:session):
    match flags:
        case 'new':
            app.new_group(args)
            
    main.create_group_file(
        url = app.urls, 
        destination=app.folder,
        file_name=app.open_file,
        overwrite=True
    )

def exit(args, flags, app:session):
    match flags:
        case 'save_new':
            save_to_file(args, 'new', app)
        case 'save':
            save_to_file(None, None, app)
            
    app.run = False
    
commands = {
    "open": open_group,
    "add" : add,
    "print": print_data,
    "save": save_to_file,
    "exit": exit
}

def init_session():
    with open('config.json', 'r', encoding='utf-8') as f:
        content = f.read()
        config = json.loads(content)
    return session(config)

def execute_command(command:dict, app:session):
    function_key = command.get('function')
    function = commands['function_key']
    flags = command.get('flags') # not fully implemented yet
    arguments = command.get('arguments')
    return function(arguments, flags, app)

def parse_command(input_line:str):
    command_match = re.match(command_syntax, input_line)
    if command_match:
        command = command_match.groupdict()
        return command

def main_loop(app:session):
    app.run = True
    input_line = input()
    while app.run:
        command = parse_command(input_line)
        if command:
            execute_command(command, app)

        input_line = input()

if __name__ == '__main__':
    app = init_session()
    main_loop(app)