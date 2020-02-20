import unittest
import os
from tempfile import TemporaryDirectory

from parser import Command, Parser


class ParserTest(unittest.TestCase):
    def setUp(self):
        self.test_dir = TemporaryDirectory()
        os.chdir(self.test_dir.name)
        print(f'now working in {self.test_dir.name}')


    def tearDown(self):
        self.test_dir.cleanup()


    def write_test_file(self, filename, contents):
        f = open(filename, 'w')
        f.write('\n'.join(contents))
        f.close()

        return f

    def test_arg1(self):
        test_filename  = 'test_arg1'
        self.write_test_file(test_filename, ['add'])

        parser = Parser(test_filename)

        self.assertTrue(parser.has_more_commands())
        parser.advance()
        self.assertEqual(parser.commandType(), Command.C_ARITHMETIC)
        self.assertEqual(parser.arg1(), 'add')
