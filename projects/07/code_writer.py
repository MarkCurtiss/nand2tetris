class CodeError(Exception):
    pass

class CodeWriter:
    def __init__(self, output):
        self.setFileName(output)


    def Close(self):
        self.output_file.close()


    def __del__(self):
        self.Close()


    def setFileName(self, output):
        self.output_file = open(output, 'w')


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
            assembly = [
                '@SP',
                'M=M-1',
                'A=M',
                'D=M',
                '@SP',
                'M=M-1',
                'A=M',
                'D=D-M',
                '@TRUE',
                'D;JEQ',

                '@FALSE',
                '0;JMP',

                '(TRUE)',
                '@SP',
                'A=M',
                'M=1',
                '@END',
                '0;JMP',

                '(FALSE)',
                '@SP',
                'A=M',
                'M=0',
                '@END',
                '0;JMP',

                '(END)'
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
