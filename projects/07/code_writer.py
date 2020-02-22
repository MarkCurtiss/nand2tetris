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
        if operator == 'add':
            self.output_file.writelines([
                '@SP\n',
                'D=M\n',
                'A=A-1\n',
                'D=D+M\n',
                'M=D\n'
            ])
            # to add
            # @SP
            # D=M
            # A=A-1 # SP -= 1
            # D=D+M
            # M=D   #RAM[SP] = results of computation

        self.output_file.flush()

    def writePushPop(self, command):
        operator, label, operand = command.split()
        if(operator == 'push'):
            # SP 0x0085 -> 0x0000
            # M[0x00000] = 7
            # M[SP] = SP+1 (SP == 0x00086)
            # @SP loads 0x00085 into the A register
            # I want RAM[RAM[SP]]

            #@SP
            #A=M (A now contains 0x0000)
            #M=7
            #A=A+1

            self.output_file.writelines([
                '@SP\n',
                'A=M\n',
                f'M={operand}\n',
                'A=A+1\n'
            ])

            self.output_file.flush()
