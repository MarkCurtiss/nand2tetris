#!/usr/local/bin/python3

import sys
import xml.etree.ElementTree as ET
import logging


from tokenizer import Tokenizer


logging.basicConfig(
    format='%(asctime)s [%(module)s] %(levelname)s:%(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %T'
)
LOGGER = logging.getLogger('compilation-engine')
LOGGER.setLevel(logging.DEBUG)


class JackCompilerError(Exception):
    pass


class JackParseError(JackCompilerError):
    pass


class CompilationEngine:
    def __init__(self):
        self.tokenizer = Tokenizer()


    def compile(self, input):
        tokens = ET.fromstring(self.tokenizer.tokenize(input))
        LOGGER.debug(f'We have {len(tokens)} tokens to visit')


        # The spec says that 'class' is the compilation unit so I we can assume we start with one.
        index = 0
        peekahead = None
        compilation_unit = ET.Element('class')

        while (index < len(tokens)):
            if index == len(tokens) - 1:
                LOGGER.debug('we are at the last element - no peeking')
                peekahead = None
            else:
                peekahead = tokens[index+1]

            token = tokens[index]
            LOGGER.debug(f'index: {index}, token: {token}, peekahead: {peekahead}')

            # main parse loop
            if self.is_class(token):
                LOGGER.debug('found a class')
                index = self.compile_class(tokens, index, compilation_unit)

            # . . .


            index += 1

        self.prettify_elements(compilation_unit)
        return ET.tostring(compilation_unit, encoding='unicode')


    def is_first_class(self, index):
        return index == 0


    def is_class(self, token):
        LOGGER.debug(f'is_class called with tag {token.tag} and text {token.text}')
        return token.tag == 'keyword' and token.text == 'class'


    def is_symbol(self, token):
        return token.tag == 'symbol'


    def is_identifier(self, token):
        return token.tag == 'identifier'


    def compile_class(self, tokens, index, compilation_unit):
        LOGGER.debug(f'In compile_class we are at index {index}')

        # <keyword> class
        #   <identifier> class name
        #   <symbol> {
        # classvariables?
        # subroutineDec?
        # }

        current_token = tokens[index]
        if (self.is_class(current_token)):
            LOGGER.debug(f'our current token is tag {current_token.tag} and text {current_token.text}')
            ET.SubElement(compilation_unit, 'keyword').text = current_token.text
            index += 1
            LOGGER.debug(f'after parsing a keyword we are at {index}')
        else:
            raise JackParseError(f'Expected a class keyword to open class but found {tokens[index]}')

        if (self.is_identifier(tokens[index])):
            index = self.compile_identifier(tokens, index, compilation_unit)
            LOGGER.debug(f'after compiling an identifier we are at {index}')
        else:
            raise JackParseError(f'Expected an identifier for class name  but found {tokens[index]}')

        if self.is_symbol(tokens[index]):
            index = self.compile_symbol(tokens, index, compilation_unit)
            LOGGER.debug(f'after compiling a symbol we are at index {index}')
        else:
            raise JackParseError(f'Expected a symbol to open class definition but found {tokens[index]}')


        # optional class variables and subroutineDec

        if self.is_symbol(tokens[index]):
            index = self.compile_symbol(tokens, index, compilation_unit)
            LOGGER.debug(f'after compiling a symbol we are at index {index}')
        else:
            raise JackParseError(f'Expected a symbol to close class definition but found {tokens[index]}')


        return index


    def compile_identifier(self, tokens, index, compilation_unit):
        current_token = tokens[index]
        ET.SubElement(compilation_unit, 'identifier').text = current_token.text
        return index+1


    def compile_symbol(self, tokens, index, compilation_unit):
        current_token = tokens[index]
        ET.SubElement(compilation_unit, 'symbol').text = current_token.text
        return index+1


    def prettify_elements(self, tree):
        return self.tokenizer.prettify_elements(tree)


if __name__ == '__main__':
    filename = sys.argv[1]

    tokenizer = Tokenizer()
    compiler = CompilationEngine()
    LOGGER.debug(f'now tokenizing file: {filename}')
    # to use against a Jack file
    # diff -w <(./tokenizer.py Square/Square.jack ) <(cat Square/SquareT.xml)
    with open(filename, 'r') as f:
        tokens = tokenizer.tokenize(''.join(f.readlines()))
        compiler.compile(tokens)
