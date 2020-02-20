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


    def test_write_arithmetic(self):
        code_writer = CodeWriter('test_output')
        code_writer.writeArithmetic('add')
