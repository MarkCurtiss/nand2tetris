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
            assembly = [x+'\n' for x in [
                '@SP',
                'A=M-1',
                'D=M',
                'A=A-1',
                'D=D+M',
                'M=D',
                'D=A+1',
                '@SP',
                'M=D'
                ]]

            self.output_file.writelines(assembly)


        self.output_file.flush()

    def writePushPop(self, command):
        operator, label, operand = command.split()
        if(operator == 'push'):
            assembly = [x+'\n' for x in [
                f'@{operand}',
                'D=A',
                '@SP',
                'A=M',
                'M=D',
                'D=A+1',
                '@SP',
                'M=D'
            ]]

            self.output_file.writelines(assembly)
            self.output_file.flush()
