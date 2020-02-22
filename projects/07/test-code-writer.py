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
        code_writer.writePushPop('push constant 8')
        code_writer.writeArithmetic('add')

        with open('test_output', 'r') as f:
            assembly = [x.rstrip() for x in f.readlines()]

            self.assertEqual(assembly, [
                # push constant 7
                '@7',
                'D=A',
                '@SP',
                'A=M',
                'M=D',
                'D=A+1',
                '@SP',
                'M=D',

                #push constant 8
                '@8',
                'D=A',
                '@SP',
                'A=M',
                'M=D',
                'D=A+1',
                '@SP',
                'M=D',

                # add
                '@SP',
                'A=M-1',
                'D=M',
                'A=A-1',
                'D=D+M',
                'M=D',
                'D=A+1',
                '@SP',
                'M=D'
            ])
