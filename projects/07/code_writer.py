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
                'A=M-1',
                'D=M',
                'A=A-1',
                'D=D+M',
                'M=D',
                'D=A+1',
                '@SP',
                'M=D'
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
                'M=1',
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

            self.output_file.writelines(assembly)
            self.output_file.flush()
