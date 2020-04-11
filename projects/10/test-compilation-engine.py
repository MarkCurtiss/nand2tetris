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


    def test_class_with_variables_and_empty_subroutine(self):
        output = self.compiler.compile("""
        class Main {
            field int size;
            function void main() { }
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
        <identifier> size </identifier>
        <symbol> ; </symbol>
    </classVarDec>
    <subroutineDec>
        <keyword> function </keyword>
        <keyword> void </keyword>
        <identifier> main </identifier>
        <symbol> ( </symbol>
        <parameterList>
        </parameterList>
        <symbol> ) </symbol>
        <subroutineBody>
          <symbol> { </symbol>
          <statements/>
          <symbol> } </symbol>
        </subroutineBody>
    </subroutineDec>
    <symbol> } </symbol>
</class>""", True
        )

    def test_subroutine_with_variables_and_no_statements(self):
        output = self.compiler.compile("""
        class Main {
            function void main() {
                var Array a;
                var int length;
                var int i, sum;
            }
        }
""")

        self.assert_xml_equal(
            output,
            """<class>
    <keyword> class </keyword>
    <identifier> Main </identifier>
    <symbol> { </symbol>
    <subroutineDec>
        <keyword> function </keyword>
        <keyword> void </keyword>
        <identifier> main </identifier>
        <symbol> ( </symbol>
        <parameterList>
        </parameterList>
        <symbol> ) </symbol>
        <subroutineBody>
          <symbol> { </symbol>
          <varDec>
            <keyword> var </keyword>
            <identifier> Array </identifier>
            <identifier> a </identifier>
            <symbol> ; </symbol>
          </varDec>
          <varDec>
            <keyword> var </keyword>
            <keyword> int </keyword>
            <identifier> length </identifier>
            <symbol> ; </symbol>
          </varDec>
          <varDec>
            <keyword> var </keyword>
            <keyword> int </keyword>
            <identifier> i </identifier>
            <symbol> , </symbol>
            <identifier> sum </identifier>
            <symbol> ; </symbol>
          </varDec>
          <statements></statements>
          <symbol> } </symbol>
        </subroutineBody>
    </subroutineDec>
    <symbol> } </symbol>
</class>""")


    def test_let_statement(self):
       output = self.compiler.compile("""
        class Main {
            function void main() {
                let i = 0;
            }
        }
""")

       self.assert_xml_equal(
            output,
            """<class>
    <keyword> class </keyword>
    <identifier> Main </identifier>
    <symbol> { </symbol>
    <subroutineDec>
        <keyword> function </keyword>
        <keyword> void </keyword>
        <identifier> main </identifier>
        <symbol> ( </symbol>
        <parameterList>
        </parameterList>
        <symbol> ) </symbol>
        <subroutineBody>
          <symbol> { </symbol>
          <statements>
              <letStatement>
                <keyword> let </keyword>
                <identifier> i </identifier>
                <symbol> = </symbol>
                <expression>
                  <term>
                    <integerConstant> 0 </integerConstant>
                  </term>
                </expression>
                <symbol> ; </symbol>
              </letStatement>
           </statements>
          <symbol> } </symbol>
        </subroutineBody>
    </subroutineDec>
    <symbol> } </symbol>
    </class>""")
