import re
import commands

default_path = 'URLs.json'
save_point, data_path, staged_data = commands.set_data_path(default_path,None)

def execute_command(command:re.Match):
    command = command.groupdict() # this allows manipulability for the command components
    function_to_exec = command.get('command')
    argument = command.get('argument')
    if function_to_exec:
        commands.commands[function_to_exec](argument, staged_data) # this line executes the command

def main_loop():
    input_line = input()
    while input_line != r'\exit':
        if command := re.match(commands.command_syntax, input_line):
            execute_command(command)

        input_line = input()
    print('function exited successfully')


if __name__ == '__main__':
    main_loop()