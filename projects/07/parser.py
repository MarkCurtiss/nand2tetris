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


    def commandType(self):
        if self.current_command in ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']:
            return Command.C_ARITHMETIC
        elif self.current_command == 'push':
            return Command.C_PUSH
        elif self.current_command == 'pop':
            return Command.C_POP
        elif self.current_command == 'label':
            return Command.C_LABEL
        elif self.current_command == 'goto':
            return Command.C_GOTO
        elif self.current_command == 'if-goto':
            return Command.C_IF
        elif self.current_command == 'function':
            return Command.C_FUNCTION
        elif self.current_command == 'return':
            return Command.C_RETURN
        elif self.current_command == 'call':
            return Command.C_CALL
        else:
            raise ParseError(f'Unrecognized command {self.current_command}')


    def arg1(self):
        if self.commandType() == Command.C_RETURN:
            raise ParseError('Do not call arg1 on command type C_RETURN')
        else:
            return self.current_command.split()[0]

   def arg2():
       if commandType() not in Command.COMMANDS_WITH_ARGS:
           raise ParseError('Do not call arg2 on commands that do not take args')
       else:
           operands = this.current_command.split()
           return operands[1]
