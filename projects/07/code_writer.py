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
            self.output_file.write('add\n')

        self.output_file.flush()

    def writePushPop(self, command):
        operator, label, operand = command.split()
        self.output_file.write(operator + '\n')
        self.output_file.write(operand + '\n')
