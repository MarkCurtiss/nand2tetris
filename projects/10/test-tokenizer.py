import unittest
import xml.etree.ElementTree as ET
import os
from tempfile import TemporaryDirectory


from tokenizer import Tokenizer


class TokenizerTest(unittest.TestCase):
    def setUp(self):
        self.tokenizer = Tokenizer()
        self.maxDiff = None


    def reformat_xml_to_standardize_whitespace(self, xml):
        tree = ET.fromstring(''.join(xml.split()))
        self.tokenizer.prettify_elements(tree)
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


    def test_if(self):
        output = self.tokenizer.tokenize("""
if (x < 0) {
   let state = "negative";
}
"""
        )

        self.assert_xml_equal(
            output,
            """<tokens>
    <keyword> if </keyword>
    <symbol> ( </symbol>
    <identifier> x </identifier>
    <symbol> &lt; </symbol>
    <integerConstant> 0 </integerConstant>
    <symbol> ) </symbol>
    <symbol> { </symbol>
    <keyword> let </keyword>
    <identifier> state </identifier>
    <symbol> = </symbol>
    <stringConstant> negative </stringConstant>
    <symbol> ; </symbol>
    <symbol> } </symbol>
</tokens>"""
        )


    def test_comments(self):
        output = self.tokenizer.tokenize("""
// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/10/ArrayTest/Main.jack

// (identical to projects/09/Average/Main.jack)

/** Computes the average of a sequence of integers. */
""")

        self.assert_xml_equal(output, '<tokens></tokens>')
