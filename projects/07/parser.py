from enum import Enum

class ParseError(Exception):
    pass


class Command(Enum):
    C_ARITHMETIC = 0
    C_PUSH = 1
    C_POP = 2
    C_LABEL = 3
    C_GOTO = 4
    C_IF = 5
    C_FUNCTION = 6
    C_RETURN = 7
    C_CALL = 8


class Parser:
    def __init__(input):
        this.input_file = open(input, 'r')
        this.next_command = None
        this.current_command = None


    def has_more_commands():
        this.next_command = f.readline()
        return this.next_command


    def advance():
        this.command = this.next_command


    def commandType():
        if this.current_command in ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']:
            return Command.C_ARITHMETIC
        elif this.current_command == 'push':
            return Command.C_PUSH
        elif this.current_command == 'pop':
            return Command.C_POP
        elif this.current_command == 'label':
            return Command.C_LABEL
        elif this.current_command == 'goto':
            return Command.C_GOTO
        elif this.current_command == 'if-goto':
            return Command.C_IF
        elif this.current_command == 'function':
            return Command.C_FUNCTION
        elif this.current_command == 'return':
            return Command.C_RETURN
        elif this.current_command == 'call':
            return Command.C_CALL
        else:
            raise ParseError(f'Unrecognized command {this.current_command}')


    def arg1():
        if commandType() == Command.C_RETURN:
            raise ParseError('Do not call arg1 on command type C_RETURN')
        else:
            operands = this.command.split()
