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

    def test_array_test(self):
        output = self.tokenizer.tokenize("""
// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/10/ArrayTest/Main.jack

// (identical to projects/09/Average/Main.jack)

/** Computes the average of a sequence of integers. */
class Main {
    function void main() {
        var Array a;
        var int length;
        var int i, sum;

	let length = Keyboard.readInt("HOW MANY NUMBERS? ");
	let a = Array.new(length);
	let i = 0;

	while (i < length) {
	    let a[i] = Keyboard.readInt("ENTER THE NEXT NUMBER: ");
	    let i = i + 1;
	}

	let i = 0;
	let sum = 0;

	while (i < length) {
	    let sum = sum + a[i];
	    let i = i + 1;
	}

	do Output.printString("THE AVERAGE IS: ");
	do Output.printInt(sum / length);
	do Output.println();

	return;
    }
}
""")

        self.assert_xml_equal(
            output,
            """<tokens>
<keyword> class </keyword>
<identifier> Main </identifier>
<symbol> { </symbol>
<keyword> function </keyword>
<keyword> void </keyword>
<identifier> main </identifier>
<symbol> ( </symbol>
<symbol> ) </symbol>
<symbol> { </symbol>
<keyword> var </keyword>
<identifier> Array </identifier>
<identifier> a </identifier>
<symbol> ; </symbol>
<keyword> var </keyword>
<keyword> int </keyword>
<identifier> length </identifier>
<symbol> ; </symbol>
<keyword> var </keyword>
<keyword> int </keyword>
<identifier> i </identifier>
<symbol> , </symbol>
<identifier> sum </identifier>
<symbol> ; </symbol>
<keyword> let </keyword>
<identifier> length </identifier>
<symbol> = </symbol>
<identifier> Keyboard </identifier>
<symbol> . </symbol>
<identifier> readInt </identifier>
<symbol> ( </symbol>
<stringConstant> HOW MANY NUMBERS?  </stringConstant>
<symbol> ) </symbol>
<symbol> ; </symbol>
<keyword> let </keyword>
<identifier> a </identifier>
<symbol> = </symbol>
<identifier> Array </identifier>
<symbol> . </symbol>
<identifier> new </identifier>
<symbol> ( </symbol>
<identifier> length </identifier>
<symbol> ) </symbol>
<symbol> ; </symbol>
<keyword> let </keyword>
<identifier> i </identifier>
<symbol> = </symbol>
<integerConstant> 0 </integerConstant>
<symbol> ; </symbol>
<keyword> while </keyword>
<symbol> ( </symbol>
<identifier> i </identifier>
<symbol> &lt; </symbol>
<identifier> length </identifier>
<symbol> ) </symbol>
<symbol> { </symbol>
<keyword> let </keyword>
<identifier> a </identifier>
<symbol> [ </symbol>
<identifier> i </identifier>
<symbol> ] </symbol>
<symbol> = </symbol>
<identifier> Keyboard </identifier>
<symbol> . </symbol>
<identifier> readInt </identifier>
<symbol> ( </symbol>
<stringConstant> ENTER THE NEXT NUMBER:  </stringConstant>
<symbol> ) </symbol>
<symbol> ; </symbol>
<keyword> let </keyword>
<identifier> i </identifier>
<symbol> = </symbol>
<identifier> i </identifier>
<symbol> + </symbol>
<integerConstant> 1 </integerConstant>
<symbol> ; </symbol>
<symbol> } </symbol>
<keyword> let </keyword>
<identifier> i </identifier>
<symbol> = </symbol>
<integerConstant> 0 </integerConstant>
<symbol> ; </symbol>
<keyword> let </keyword>
<identifier> sum </identifier>
<symbol> = </symbol>
<integerConstant> 0 </integerConstant>
<symbol> ; </symbol>
<keyword> while </keyword>
<symbol> ( </symbol>
<identifier> i </identifier>
<symbol> &lt; </symbol>
<identifier> length </identifier>
<symbol> ) </symbol>
<symbol> { </symbol>
<keyword> let </keyword>
<identifier> sum </identifier>
<symbol> = </symbol>
<identifier> sum </identifier>
<symbol> + </symbol>
<identifier> a </identifier>
<symbol> [ </symbol>
<identifier> i </identifier>
<symbol> ] </symbol>
<symbol> ; </symbol>
<keyword> let </keyword>
<identifier> i </identifier>
<symbol> = </symbol>
<identifier> i </identifier>
<symbol> + </symbol>
<integerConstant> 1 </integerConstant>
<symbol> ; </symbol>
<symbol> } </symbol>
<keyword> do </keyword>
<identifier> Output </identifier>
<symbol> . </symbol>
<identifier> printString </identifier>
<symbol> ( </symbol>
<stringConstant> THE AVERAGE IS:  </stringConstant>
<symbol> ) </symbol>
<symbol> ; </symbol>
<keyword> do </keyword>
<identifier> Output </identifier>
<symbol> . </symbol>
<identifier> printInt </identifier>
<symbol> ( </symbol>
<identifier> sum </identifier>
<symbol> / </symbol>
<identifier> length </identifier>
<symbol> ) </symbol>
<symbol> ; </symbol>
<keyword> do </keyword>
<identifier> Output </identifier>
<symbol> . </symbol>
<identifier> println </identifier>
<symbol> ( </symbol>
<symbol> ) </symbol>
<symbol> ; </symbol>
<keyword> return </keyword>
<symbol> ; </symbol>
<symbol> } </symbol>
<symbol> } </symbol>
</tokens>
            """)

    def test_class(self):
        output = self.tokenizer.tokenize("""
class Square {

   field int x, y; // screen location of the square's top-left corner
   field int size; // length of this square, in pixels

   /** Constructs a new square with a given location and size. */
   constructor Square new(int Ax, int Ay, int Asize) {
      let x = Ax;
      let y = Ay;
      let size = Asize;
      do draw();
      return this;
   }""")

        self.assert_xml_equal(
            output,
            """
<tokens>
<keyword> class </keyword>
<identifier> Square </identifier>
<symbol> { </symbol>
<keyword> field </keyword>
<keyword> int </keyword>
<identifier> x </identifier>
<symbol> , </symbol>
<identifier> y </identifier>
<symbol> ; </symbol>
<keyword> field </keyword>
<keyword> int </keyword>
<identifier> size </identifier>
<symbol> ; </symbol>
<keyword> constructor </keyword>
<identifier> Square </identifier>
<identifier> new </identifier>
<symbol> ( </symbol>
<keyword> int </keyword>
<identifier> Ax </identifier>
<symbol> , </symbol>
<keyword> int </keyword>
<identifier> Ay </identifier>
<symbol> , </symbol>
<keyword> int </keyword>
<identifier> Asize </identifier>
<symbol> ) </symbol>
<symbol> { </symbol>
<keyword> let </keyword>
<identifier> x </identifier>
<symbol> = </symbol>
<identifier> Ax </identifier>
<symbol> ; </symbol>
<keyword> let </keyword>
<identifier> y </identifier>
<symbol> = </symbol>
<identifier> Ay </identifier>
<symbol> ; </symbol>
<keyword> let </keyword>
<identifier> size </identifier>
<symbol> = </symbol>
<identifier> Asize </identifier>
<symbol> ; </symbol>
<keyword> do </keyword>
<identifier> draw </identifier>
<symbol> ( </symbol>
<symbol> ) </symbol>
<symbol> ; </symbol>
<keyword> return </keyword>
<keyword> this </keyword>
<symbol>;</symbol>
<symbol>}</symbol>
</tokens>
            """)


    def test_while(self):
      output = self.tokenizer.tokenize("""
      while (~exit) {
""")

      self.assert_xml_equal(
          output,
          """
<tokens>
<keyword> while </keyword>
<symbol> ( </symbol>
<symbol> ~ </symbol>
<identifier> exit </identifier>
<symbol> ) </symbol>
<symbol> { </symbol>
</tokens>
          """)
