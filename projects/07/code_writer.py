import os

class CodeError(Exception):
    pass

offset_by_label = {
    'local': 'LCL',
    'argument': 'ARG',
    'this': 'THIS',
    'that': 'THAT',
    'temp': '5' #tmp starts at RAM[5] and runs to RAM[12]
}


class CodeWriter:
    def __init__(self, output):
        self.file_name = None
        self.label_count = 0
        self.setFileName(output)

    def Close(self):
        self.output_file.close()


    def __del__(self):
        self.Close()

    def make_label(self):
        label = f'{os.path.basename(self.file_name)}.{self.label_count}'
        self.label_count += 1
        return label


    def setFileName(self, output):
        self.file_name = output
        self.output_file = open(self.file_name, 'w')


    def writeArithmetic(self, operator):
        assembly = []
        if operator == 'add':
            assembly = [
                '@SP',
                'M=M-1',
                'A=M',
                'D=M',
                '@SP',
                'M=M-1',
                'A=M',
                'D=D+M',
                'M=D',
                '@SP',
                'M=M+1'
            ]
        elif operator == 'sub':
            assembly = [
                '@SP',
                'M=M-1',
                'A=M',
                'D=M',
                '@SP',
                'M=M-1',
                'A=M',
                'D=M-D',
                'M=D',
                '@SP',
                'M=M+1'
            ]
        elif operator == 'neg':
            assembly = [
                '@SP',
                'M=M-1',
                'A=M',
                'M=-M',
                '@SP',
                'M=M+1'
            ]
        elif operator == 'and':
            assembly = [
                '@SP',
                'M=M-1',
                'A=M',
                'D=M',
                '@SP',
                'M=M-1',
                'A=M',
                'M=M&D',
                '@SP',
                'M=M+1'
            ]
        elif operator == 'or':
            assembly = [
                '@SP',
                'M=M-1',
                'A=M',
                'D=M',
                '@SP',
                'M=M-1',
                'A=M',
                'M=M|D',
                '@SP',
                'M=M+1'
            ]
        elif operator == 'not':
            assembly = [
                '@SP',
                'M=M-1',
                'A=M',
                'M=!M',
                '@SP',
                'M=M+1'
            ]
        elif operator == 'eq':
            (false_label, true_label, end_label)  = [self.make_label() for x in range(3)]

            assembly = [
                '@SP',
                'M=M-1',
                'A=M',
                'D=M',
                '@SP',
                'M=M-1',
                'A=M',
                'D=D-M',
                f'@{true_label}',
                'D;JEQ',

                f'@{false_label}',
                '0;JMP',

                f'({true_label})',
                '@SP',
                'A=M',
                'M=-1',
                f'@{end_label}',
                '0;JMP',

                f'({false_label})',
                '@SP',
                'A=M',
                'M=0',
                f'@{end_label}',
                '0;JMP',

                f'({end_label})',
                '@SP',
                'M=M+1'
            ]
        elif operator == 'lt':
            (false_label, true_label, end_label)  = [self.make_label() for x in range(3)]
            assembly = [
                '@SP',
                'M=M-1',
                'A=M',
                'D=M',   #y
                '@SP',
                'M=M-1',
                'A=M',
                'D=M-D', #x - y
                f'@{true_label}',
                'D;JLT',

                f'@{false_label}',
                '0;JMP',

                f'({true_label})',
                '@SP',
                'A=M',
                'M=-1',
                f'@{end_label}',
                '0;JMP',

                f'({false_label})',
                '@SP',
                'A=M',
                'M=0',
                f'@{end_label}',
                '0;JMP',

                f'({end_label})',
                '@SP',
                'M=M+1'
            ]
        elif operator == 'gt':
            (false_label, true_label, end_label)  = [self.make_label() for x in range(3)]
            assembly = [
                '@SP',
                'M=M-1',
                'A=M',
                'D=M',   #y
                '@SP',
                'M=M-1',
                'A=M',
                'D=D-M', #y - x
                f'@{true_label}',
                'D;JLT',

                f'@{false_label}',
                '0;JMP',

                f'({true_label})',
                '@SP',
                'A=M',
                'M=-1',
                f'@{end_label}',
                '0;JMP',

                f'({false_label})',
                '@SP',
                'A=M',
                'M=0',
                f'@{end_label}',
                '0;JMP',

                f'({end_label})',
                '@SP',
                'M=M+1'
            ]


        self.output_file.writelines([x + '\n' for x in assembly])
        self.output_file.flush()

    def writePushPop(self, command):
        operator, label, operand = command.split()
        assembly = []

        if(operator == 'push'):
            isConstant = False
            isPointer = False
            isStatic = False

            if label == 'constant':
                isConstant = True
            elif label in offset_by_label:
                offset_ptr = offset_by_label[label]
            elif label == 'static':
                isStatic = True
            elif label == 'pointer':
                isPointer = True
            else:
                raise CodeError(f'Unrecognized label {label} passed to push (command was {command})')

            if isPointer:
                address = ''
                if int(operand) == 0:
                    address = 'THIS'
                elif int(operand) == 1:
                    address = 'THAT'
                else:
                    raise CodeError(f'Unrecognized push pointer combination (command was {command})')

                assembly = [
                    f'@{address}',
                    'D=M',
                    '@SP',
                    'A=M',
                    'M=D',
                    '@SP',
                    'M=M+1'
                ]
            elif isStatic:
                static_label = f'{os.path.basename(self.file_name)}.{operand}'
                assembly = [
                    f'@{static_label}',
                    'D=M',
                    '@SP',
                    'A=M',
                    'M=D',
                    '@SP',
                    'M=M+1'
                ]
            elif isConstant:
                assembly = [
                    f'@{operand}', # put constant in A
                    'D=A',         # D = constant
                    '@SP',         # 0 in A
                    'A=M',         # A == 256
                    'M=D',         # RAM[256] = constant
                    '@SP',         # A == 256
                    'M=M+1'        # RAM[0] == 256
                ]
            else:
                get_base = ''
                if label == 'temp':
                    get_base = 'D=A'
                else:
                    get_base = 'D=M'

                assembly = [
                    f'@{offset_ptr}', #A = base of segment
                    f'{get_base}',
                    f'@{operand}', # A = offset
                    'D=A+D',       # D is now the destination address
                    'A=D',         # A is now the address
                    'D=M',         # D has the value

                    '@SP',
                    'A=M',         # A == 256
                    'M=D',         # RAM[256] = value from stack
                    '@SP',         # A == 256
                    'M=M+1'        # RAM[0] == 256
                ]

        elif (operator == 'pop'):
            is_pointer = False
            offset_ptr = ''
            isStatic = False

            if label in offset_by_label:
                offset_ptr = offset_by_label[label]
            elif label == 'pointer':
                is_pointer = True
            elif label == 'static':
                isStatic = True
            else:
                raise CodeError(f'Unrecognized label {label} passed to pop (command was {command})')

            if is_pointer:
                address = ''
                if int(operand) == 0:
                    address = 'THIS'
                elif int(operand) == 1:
                    address = 'THAT'
                else:
                    raise CodeError(f'Unrecognized pop pointer combination (command was {command})')

                assembly = [
                    '@SP',
                    'M=M-1',
                    'A=M',
                    'D=M',  #D holds the pop'ed value
                    f'@{address}',
                    'M=D'
                ]
            elif isStatic:
                static_label = f'{os.path.basename(self.file_name)}.{operand}'
                assembly = [
                    '@SP',
                    'M=M-1',
                    'A=M',
                    'D=M',  #D holds the pop'ed value
                    f'@{static_label}',
                    'M=D'
                ]
            else:
                get_base = ''
                if label == 'temp':
                    get_base = 'D=A'
                else:
                    get_base = 'D=M'

                assembly = [
                    f'@{offset_ptr}', #A = base of segment
                    get_base,
                    f'@{operand}', # A = offset
                    'D=A+D',       # D is now the destination address
                    '@R13',
                    'M=D',  # R13 has the address
                    '@SP',
                    'M=M-1',
                    'A=M',
                    'D=M',  #D holds the pop'ed value

                    '@R13',
                    'A=M',
                    'M=D'
                ]


        self.output_file.writelines([x + '\n' for x in assembly])
        self.output_file.flush()
