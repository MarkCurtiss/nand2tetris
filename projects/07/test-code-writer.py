import unittest
import os
from tempfile import TemporaryDirectory

from code_writer import CodeWriter

class CodeWriterTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = TemporaryDirectory()
        os.chdir(self.tmpdir.name)
        print(f'now working in {self.tmpdir.name}')

    def __del__(self):
        self.tmpdir.cleanup()


    def test_simple_add(self):
        code_writer = CodeWriter('test_output')
        code_writer.writePushPop('push constant 7')
        # code_writer.writePushPop('push constant 8')
        code_writer.writeArithmetic('add')

        with open('test_output', 'r') as f:
            assembly = f.readlines()

            #@SP
            #D=A
            #M=7

            self.assertEqual(assembly, [
                '@SP\n',
                'D=A\n',
                'M=7\n',
                'add\n'
            ])
