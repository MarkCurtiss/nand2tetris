import unittest
import os
from tempfile import TemporaryDirectory

from code_writer import CodeWriter

class CodeWriterTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = TemporaryDirectory()
        os.chdir(self.tmpdir.name)
        self.assembly_filename = 'test_output'
        self.code_writer = CodeWriter(self.assembly_filename)


    def __del__(self):
        self.tmpdir.cleanup()


    def test_add(self):
        self.code_writer.writeArithmetic('add')
        self.assertGeneratedAssemblyEqual([
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
        ])


    def test_sub(self):
        self.code_writer.writeArithmetic('sub')
        self.assertGeneratedAssemblyEqual([
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
        ])


    def test_neq(self):
        self.code_writer.writeArithmetic('neg')
        self.assertGeneratedAssemblyEqual([
            '@SP',
            'M=M-1',
            'A=M',
            'M=-M',
            '@SP',
            'M=M+1'
        ])


    def test_and(self):
        self.code_writer.writeArithmetic('and')
        self.assertGeneratedAssemblyEqual([
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
        ])


    def test_or(self):
        self.code_writer.writeArithmetic('or')
        self.assertGeneratedAssemblyEqual([
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
        ])


    def test_not(self):
        self.code_writer.writeArithmetic('not')
        self.assertGeneratedAssemblyEqual([
            '@SP',
            'M=M-1',
            'A=M',
            'M=!M',
            '@SP',
            'M=M+1'
        ])


    def test_eq(self):
        self.code_writer.writeArithmetic('eq')
        self.assertGeneratedAssemblyEqual([
            '@SP',
            'M=M-1',
            'A=M',
            'D=M',
            '@SP',
            'M=M-1',
            'A=M',
            'D=D-M',
            '@test_output.1',
            'D;JEQ',

            '@test_output.0',
            '0;JMP',

            '(test_output.1)',
            '@SP',
            'A=M',
            'M=-1',
            '@test_output.2',
            '0;JMP',

            '(test_output.0)',
            '@SP',
            'A=M',
            'M=0',
            '@test_output.2',
            '0;JMP',

            '(test_output.2)',
            '@SP',
            'M=M+1'
        ])


    def test_lt(self):
        self.code_writer.writeArithmetic('lt')
        self.assertGeneratedAssemblyEqual([
            '@SP',
            'M=M-1',
            'A=M',
            'D=M',
            '@SP',
            'M=M-1',
            'A=M',
            'D=M-D',
            '@test_output.1',
            'D;JLT',

            '@test_output.0',
            '0;JMP',

            '(test_output.1)',
            '@SP',
            'A=M',
            'M=-1',
            '@test_output.2',
            '0;JMP',

            '(test_output.0)',
            '@SP',
            'A=M',
            'M=0',
            '@test_output.2',
            '0;JMP',

            '(test_output.2)',
            '@SP',
            'M=M+1'
        ])


    def test_gt(self):
        self.code_writer.writeArithmetic('gt')
        self.assertGeneratedAssemblyEqual([
            '@SP',
            'M=M-1',
            'A=M',
            'D=M',
            '@SP',
            'M=M-1',
            'A=M',
            'D=D-M',
            '@test_output.1',
            'D;JLT',

            '@test_output.0',
            '0;JMP',

            '(test_output.1)',
            '@SP',
            'A=M',
            'M=-1',
            '@test_output.2',
            '0;JMP',

            '(test_output.0)',
            '@SP',
            'A=M',
            'M=0',
            '@test_output.2',
            '0;JMP',

            '(test_output.2)',
            '@SP',
            'M=M+1'
        ])


    def assertGeneratedAssemblyEqual(self, assembly=[]):
        self.assertAssemblyEqual(self.assembly_filename, assembly)


    def assertAssemblyEqual(self, file_name, assembly=[]):
        with open(file_name, 'r') as f:
            self.assertEqual([x.rstrip() for x in f.readlines()], assembly)
