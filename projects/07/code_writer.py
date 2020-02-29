import os

class CodeError(Exception):
    pass

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
            assembly = [x+'\n' for x in [
                f'@{operand}', # put constant in A
                'D=A',         # D = constant
                '@SP',         # 0 in A
                'A=M',         # A == 256
                'M=D',         # RAM[256] = constant
                '@SP',         # A == 256
                'M=M+1'        # RAM[0] == 256
            ]]


        elif (operator == 'pop'):
            # pop the stack
            # push it to the offset + the address
            offset_ptr = ''
            if label == 'local':
                offset_ptr = 'LCL'
            elif label == 'argument':
                offset_ptr = 'ARG'
            elif label == 'this':
                offset_ptr = 'THIS'
            elif label == 'that':
                offset_ptr = 'THAT'
            elif label == 'temp':
                offset_ptr = '@5' #tmp starts at RAM[5] and runs to RAM[12]

            assembly = [
                '@SP',
                'M=M-1',
                'A=M',
                'D=M',  #D = RAM[SP]
                '@R13',
                'M=D',  #R13 holds the pop'ed value
                f'@{offset_ptr}', #A = base of segment
                'A=M'
                'D=M',
                f'@{operand}', #A = offset
                'D=A+D', #D is now the destination address
                '@R14'
                'M=D',  #R14 holds the destination address
                '@R13',
                'D=M',  # now has the popped value
                '@R14',
                'A=M'
        ]


        self.output_file.writelines([x + '\n' for x in assembly])
        self.output_file.flush()
