import unittest
import os
from tempfile import TemporaryDirectory

from tokenizer import Tokenizer

class TokenizerTest(unittest.TestCase):
    def setUp(self):
        self.tokenizer = Tokenizer()
        self.maxDiff = None


    def test_if(self):
        output = self.tokenizer.tokenize("""
if (x < 0) {
   let state = "negative";
}
"""
        )

        self.assertMultiLineEqual(
            (output),
            ''.join("""<tokens>
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
</tokens>""".split())
        )
