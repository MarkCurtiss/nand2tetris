from enum import Enum

# pg 144

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
        this.curent_command = None


    def has_more_commands():
        this.next_command = f.readline()
        return this.next_command


    def advance():
        this.command = this.next_command


    def commandType():
        # check current command and return a type
        pass
