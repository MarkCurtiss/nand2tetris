class CodeError(Exception):
    pass

class CodeWriter:
    def __init__(self, output):
        self.setFileName(output)


    def __del__(self):
        self.output_file.close()


    def setFileName(self, output):
        self.output_file = open(output, 'w')
