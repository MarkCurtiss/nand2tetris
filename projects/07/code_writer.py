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


    def make_incrementing_label(self):
        label = f'{os.path.basename(self.file_name)}.{self.label_count}'
        self.label_count += 1
        return label


    def uniquify_label(self, label):
        return f'{os.path.basename(self.file_name)}.{label}'


    def setFileName(self, output):
        self.file_name = output
        self.output_file = open(self.file_name, 'w')


    def advanceStackPointer(self):
        return ['@SP', 'M=M+1']


    def popStackToD(self, d_assignment='D=M'):
        return ['@SP', 'M=M-1', 'A=M', d_assignment]


    def compare(self, condition_for_jmp):
        (false_label, true_label, end_label)  = [self.make_incrementing_label() for x in range(3)]
        return [
            f'@{true_label}',
            f'{condition_for_jmp}',

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

            f'({end_label})'
        ]


    def assignStackFrom(self, from_value):
        return [
            f'@{from_value}',
            'D=M',
            '@SP',
            'A=M',
            'M=D'
        ]


    def writeArithmetic(self, operator):
        assembly = []
        if operator == 'add':
            assembly = [
                *self.popStackToD(),
                *self.popStackToD(d_assignment='D=D+M'),
                'M=D',
                *self.advanceStackPointer()
            ]
        elif operator == 'sub':
            assembly = [
                *self.popStackToD(),
                *self.popStackToD(d_assignment='D=M-D'),
                'M=D',
                *self.advanceStackPointer()
        ]
        elif operator == 'neg':
            assembly = [
                *self.popStackToD(d_assignment='M=-M'),
                *self.advanceStackPointer()
            ]
        elif operator == 'and':
            assembly = [
                *self.popStackToD(),
                *self.popStackToD(d_assignment='M=M&D'),
                *self.advanceStackPointer()
            ]
        elif operator == 'or':
            assembly = [
                *self.popStackToD(),
                *self.popStackToD(d_assignment='M=M|D'),
                *self.advanceStackPointer()
            ]
        elif operator == 'not':
            assembly = [
                *self.popStackToD(d_assignment='M=!M'),
                *self.advanceStackPointer()
            ]

        elif operator == 'eq':
            assembly = [
                *self.popStackToD(),
                *self.popStackToD(d_assignment='D=D-M'),
                *self.compare('D;JEQ'),
                *self.advanceStackPointer()
            ]
        elif operator == 'lt':
            assembly = [
                *self.popStackToD(),
                *self.popStackToD(d_assignment='D=M-D'),
                *self.compare('D;JLT'),
                *self.advanceStackPointer()
            ]
        elif operator == 'gt':
            assembly = [
                *self.popStackToD(),
                *self.popStackToD(d_assignment='D=D-M'),
                *self.compare('D;JLT'),
                *self.advanceStackPointer()
            ]

        self.write_assembly(assembly)


    def writePushPop(self, command):
        operator, label, operand, *trailing = command.split()
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
                    *self.assignStackFrom(address),
                    *self.advanceStackPointer()
                ]
            elif isStatic:
                static_label = f'{os.path.basename(self.file_name)}.{operand}'
                assembly = [
                    *self.assignStackFrom(static_label),
                    *self.advanceStackPointer()
                ]
            elif isConstant:
                assembly = [
                    f'@{operand}', # put constant in A
                    'D=A',         # D = constant
                    '@SP',         # 0 in A
                    'A=M',         # A == 256
                    'M=D',         # RAM[256] = constant
                    *self.advanceStackPointer()
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
                    *self.advanceStackPointer()
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
                    *self.popStackToD(),
                    f'@{address}',
                    'M=D'
                ]
            elif isStatic:
                static_label = f'{os.path.basename(self.file_name)}.{operand}'
                assembly = [
                    *self.popStackToD(),
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

        self.write_assembly(assembly)


    def writeLabel(self, label):
        unique_label = self.uniquify_label(label)
        self.write_assembly([f'({unique_label})'])


    def writeIf(self, label):
        unique_label = self.uniquify_label(label)
        assembly = [
            *self.popStackToD(),
            f'@{unique_label}',
            'D;JNE'
        ]
        self.write_assembly(assembly)


    def writeGoto(self, label):
        unique_label = self.uniquify_label(label)
        assembly = [
            f'@{unique_label}',
            '0;JMP'
        ]

        self.write_assembly(assembly)


    def writeFunction(self, command):
        operator, function_name, num_args, *trailing = command.split()
        unique_function_name = self.uniquify_label(function_name)
        arg_pushes = []
        assembly = [
            f'({unique_function_name})',
        ]

        for var in range(int(num_args)):
            assembly += [
                '@LCL', #A = 1
                'D=M',  #D = 305
                'A=D',  #A = 305
                'M=0',  #RAM[305]=0
                *self.advanceStackPointer()
            ]


        self.write_assembly(assembly)


    def writeReturn(self):
        # FRAME = LCL  // FRAME is a temporary variable
        # RET = *(FRAME-5) // put the return-address in a temp var
        # *ARG = pop()   // reposition the value for the caller
        # SP = ARG+1    // restore SP of the caller
        # THAT = *(FRAME-1)  // restore THAT of the caller
        # THIS = *(FRAME-2)   // restore THIS of the caller
        # ARG = *(FRAME-3)  // restore ARG of the caller
        # LCL = *(FRAME-4)  //  restore LCL of the caller
        # goto RET   // goto return-address (in the caller's code)
        assembly = [
            '@LCL',
            'D=M',
            '@R13',
            'M=D',      # FRAME=LCL
            'D=D-1',
            'D=D-1',
            'D=D-1',
            'D=D-1',
            'D=D-1',
            'A=D',
            'D=M',      # D = *(FRAME-5)
            '@R14',
            'M=D',     # put the return-address in a temp var
            *self.popStackToD(),
            '@ARG',
            'M=D',   #*ARG = pop() ?
            '@ARG',
            'D=A+1',
            'D=M',   # D == ARG+1
            '@SP',
            'M=D',   # *SP == ARG+1
            '@R13',
            'M=M-1', # FRAME-1
            'D=M',
            '@THAT',
            'M=D',# THAT = *(FRAME-1)  // restore THAT of the caller
            '@R13',
            'M=M-1',
            'D=M',
            '@THIS',
            'M=D',         # THIS = *(FRAME-2)   // restore THIS of the caller
            '@R13',
            'M=M-1',
            'D=M',
            '@ARG',
            'M=D',         # ARG = *(FRAME-3)  // restore ARG of the caller
            '@R13',
            'M=M-1',
            'D=M',
            '@LCL',
            'M=D',   # LCL = *(FRAME-4)  //  restore LCL of the caller
            '@R14',
            'A=M',
            '0;JMP' # goto RET   // goto return-address (in the caller's code)
        ]

        # line 95

        self.write_assembly(assembly)


    def write_assembly(self, assembly=[]):
        self.output_file.writelines([x + '\n' for x in assembly])
        self.output_file.flush()
