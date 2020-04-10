import unittest
import xml.etree.ElementTree as ET
import os
from tempfile import TemporaryDirectory


from compilation_engine import CompilationEngine


class CompilationEngineTest(unittest.TestCase):
    def setUp(self):
        self.compiler = CompilationEngine()
        self.maxDiff = None


    def reformat_xml_to_standardize_whitespace(self, xml):
        tree = ET.fromstring(''.join(xml.split()))
        self.compiler.prettify_elements(tree)
        return ET.tostring(tree, encoding='unicode')


    def assert_xml_equal(self, actual_xml, expected_xml, debug_output=False):
        if debug_output:
            print('expected_xml:')
            print(self.reformat_xml_to_standardize_whitespace(expected_xml))
            print('actual_xml:')
            print(self.reformat_xml_to_standardize_whitespace(actual_xml))

        self.assertEqual(
            self.reformat_xml_to_standardize_whitespace(expected_xml),
            self.reformat_xml_to_standardize_whitespace(actual_xml)
        )


    def test_empty_class(self):
        output = self.compiler.compile("""
class Main { } 
"""
        )

        self.assert_xml_equal(
            output,
            """<class>
    <keyword> class </keyword>
    <identifier> Main </identifier>
    <symbol> { </symbol>
    <symbol> } </symbol>
    </class>""")


    def test_class_with_class_variables(self):
        output = self.compiler.compile("""
        class Main {
            field int x, y;
            field int size;
            static boolean test;
            field Square square;
        }
""")

        self.assert_xml_equal(
            output,
            """<class>
    <keyword> class </keyword>
    <identifier> Main </identifier>
    <symbol> { </symbol>
    <classVarDec>
        <keyword> field </keyword>
        <keyword> int </keyword>
        <identifier> x </identifier>
        <symbol> , </symbol>
        <identifier> y </identifier>
        <symbol> ; </symbol>
    </classVarDec>
    <classVarDec>
        <keyword> field </keyword>
        <keyword> int </keyword>
        <identifier> size </identifier>
        <symbol> ; </symbol>
    </classVarDec>
    <classVarDec>
        <keyword> static </keyword>
        <keyword> boolean </keyword>
        <identifier> test </identifier>
        <symbol> ; </symbol>
    </classVarDec>
    <classVarDec>
        <keyword> field </keyword>
        <identifier> Square </identifier>
        <identifier> square </identifier>
        <symbol> ; </symbol>
    </classVarDec>
    <symbol> } </symbol>
    </class>""")    
