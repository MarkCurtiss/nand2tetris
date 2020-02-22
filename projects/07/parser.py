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

    COMMANDS_WITH_ARGS = [C_PUSH, C_POP, C_FUNCTION, C_CALL]


class Parser:
    def __init__(self, input):
        self.input_file = open(input, 'r')
        self.next_command = None
        self.current_command = None


    def __del__(self):
        self.input_file.close()


    def has_more_commands(self):
        self.next_command = self.input_file.readline()
        return self.next_command


    def advance(self):
        self.current_command = self.next_command
        return self.current_command


    def commandType(self):
        if self.current_command == 'return':
            return Command.C_RETURN

        operator = self.arg1()

        if operator in ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']:
            return Command.C_ARITHMETIC
        elif operator == 'push':
            return Command.C_PUSH
        elif operator == 'pop':
            return Command.C_POP
        elif operator == 'label':
            return Command.C_LABEL
        elif operator == 'goto':
            return Command.C_GOTO
        elif operator == 'if-goto':
            return Command.C_IF
        elif operator == 'function':
            return Command.C_FUNCTION
        elif operator == 'return':
            return Command.C_RETURN
        elif operator == 'call':
            return Command.C_CALL


    def arg1(self):
        if self.current_command and not self.current_command.isspace():
            return self.current_command.split()[0]


    def arg2(self):
       if commandType() not in Command.COMMANDS_WITH_ARGS:
           raise ParseError('Do not call arg2 on commands that do not take args')
       else:
           operands = this.current_command.split()
           return operands[1]
