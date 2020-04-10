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


    def is_keyword(self, token):
        return token.tag == 'keyword'


    def is_comma(self, token):
        return token.tag == 'symbol' and token.text == ','


    def is_closing_paren(self, token):
        return token.tag == 'symbol' and token.text == ')'


    def is_class_var(self, token):
        return self.is_keyword(token) and token.text in ['static', 'field']


    def is_subroutine_declaration(self, token):
        return self.is_keyword(token) and token.text in ['function', 'constructor', 'method']


    def is_var(self, token):
        return self.is_keyword(token) and token.text == 'var'


    def is_statement(self, token):
        return self.is_keyword(token) and token.text in ['let' ,'if', 'while', 'do', 'return']


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
            raise JackParseError(f'Expected a class keyword to open class but found {tokens[index].tag , tokens[index].text}')

        if (self.is_identifier(tokens[index])):
            index = self.compile_identifier(tokens, index, compilation_unit)
            LOGGER.debug(f'after compiling an identifier we are at {index}')
        else:
            raise JackParseError(f'Expected an identifier for class name  but found {tokens[index].tag , tokens[index].text}')

        if self.is_symbol(tokens[index]):
            index = self.compile_symbol(tokens, index, compilation_unit)
            LOGGER.debug(f'after compiling a symbol we are at index {index}')
        else:
            raise JackParseError(f'Expected a symbol to open class definition but found {tokens[index].tag , tokens[index].text}')


        # optional class variables and subroutineDec
        LOGGER.debug(f'our next token up is {tokens[index].tag , tokens[index].text}')
        while(not self.is_symbol(tokens[index])):
            LOGGER.debug(f'Have not reached the end of class variables and subroutines yet; current token is {tokens[index].tag , tokens[index].text}')
            if self.is_class_var(tokens[index]):
                index = self.compile_class_var(tokens, index, compilation_unit)
                LOGGER.debug(f'after compiling a class variable we are at index {index}')
            elif self.is_subroutine_declaration(tokens[index]):
                index = self.compile_subroutine_declaration(tokens, index, compilation_unit)
                LOGGER.debug(f'after compiling a subroutine we are at index {index}')


        if self.is_symbol(tokens[index]):
            index = self.compile_symbol(tokens, index, compilation_unit)
            LOGGER.debug(f'after compiling a symbol we are at index {index}')
        else:
            raise JackParseError(f'Expected a symbol to close class definition but found {tokens[index].tag , tokens[index].text}')


        return index


    def compile_identifier(self, tokens, index, compilation_unit):
        current_token = tokens[index]
        ET.SubElement(compilation_unit, 'identifier').text = current_token.text
        return index+1


    def compile_keyword(self,  tokens, index, compilation_unit):
        current_token = tokens[index]
        ET.SubElement(compilation_unit, 'keyword').text = current_token.text
        return index+1


    def compile_symbol(self, tokens, index, compilation_unit):
        current_token = tokens[index]
        ET.SubElement(compilation_unit, 'symbol').text = current_token.text
        return index+1


    def compile_class_var(self, tokens, index, compilation_unit):
        LOGGER.debug(f'compile_class_var: index is {index}')
        LOGGER.debug(f'compiling a class var with token {tokens[index].tag , tokens[index].text}')
        class_variable_unit = ET.SubElement(compilation_unit, 'classVarDec')
        # keyword | keyword  keyword identifier   symbol identifier symbol
        # (static | field)   type    varName    (','     varname)* ';'


        # storage type is a keyword
        current_token = tokens[index]
        if (not self.is_keyword(tokens[index])):
            raise JackParseError(f'Expected a storage type to start a variable, but found {current_token.tag , current_token.text}')

        index = self.compile_keyword(tokens, index, class_variable_unit)
        LOGGER.debug(f'compile_class_var: after compiling storage type, index is {index}')

        # type is a keyword (int, char, boolean) or an identifier (className)
        current_token = tokens[index]
        if (self.is_keyword(current_token)):
            index = self.compile_keyword(tokens, index, class_variable_unit)
            LOGGER.debug(f'compile_class_var: after compiling variable type, index is {index}')
        elif (self.is_identifier(current_token)):
            index = self.compile_identifier(tokens, index, class_variable_unit)
            LOGGER.debug(f'compile_class_var: after compiling variable type, index is {index}')
        else:
            raise JackParseError(f'Expected a variable type after a static/field token, but found {current_token.tag , current_token.text}')


        # variable name is an identifier
        current_token = tokens[index]
        if (not self.is_identifier(current_token)):
            raise JackParseError(f'Expected an identifier after a variable type, but found {current_token.tag , current_token.text}')

        index = self.compile_identifier(tokens, index, class_variable_unit)
        LOGGER.debug(f'compile_class_var: after compiling variable name, index is {index}')

        # , or ;
        current_token = tokens[index]
        LOGGER.debug(f'compile_class_var: now we are at {current_token.tag , current_token.text}')
        if (not self.is_symbol(current_token)):
            raise JackParseError(f'Expected a , or ; after a variable name, but found {current_token.tag , current_token.text }')

        while (self.is_comma(tokens[index])):
            index = self.compile_symbol(tokens, index, class_variable_unit)
            LOGGER.debug(f'compile_class_var: after compiling a , index is {index}')
            index = self.compile_identifier(tokens, index, class_variable_unit)
            LOGGER.debug(f'compile_class_var: after compiling a variable name index is {index}')

        # ;
        if not (self.is_symbol(current_token)):
            raise JackParseError(f'Expected a ; after variable declaration, but found {current_token.tag , current_token.text}')

        index = self.compile_symbol(tokens, index, class_variable_unit)

        return index


    def compile_subroutine_declaration(self, tokens, index, compilation_unit):
        LOGGER.debug(f'compile_subroutine_declaration: index is {index}')
        LOGGER.debug(f'compiling a subroutine with token {tokens[index].tag , tokens[index].text}')
        subroutine_unit = ET.SubElement(compilation_unit, 'subroutineDec')
        #  keyword       keyword    keyword  kw     id    identifier     sym ..            sym ...
        # (constructor | function | method) (void | type) subRoutineNmae '(' parameterList ')' subRoutineBody

        # function type
        index = self.compile_keyword(tokens, index, subroutine_unit)

        # return type
        current_token = tokens[index]
        if (self.is_keyword(current_token)):
            index = self.compile_keyword(tokens, index, subroutine_unit)
        elif (self.is_identifier(current_token)):
            index = self.compile_identifier(tokens, index, subroutine_unit)
        else:
            raise JackParseError(f'expected a keyword or identifier after a method declaration but found {current_token.tag , current_token.text}')

        # function name
        index = self.compile_identifier(tokens, index, subroutine_unit)
        # ( parameter list )
        index = self.compile_symbol(tokens, index, subroutine_unit)
        index = self.compile_parameter_list(tokens, index, subroutine_unit)
        index = self.compile_symbol(tokens, index, subroutine_unit)

        index = self.compile_subroutine_body(tokens, index, subroutine_unit)

        return index


    def compile_parameter_list(self, tokens, index, compilation_unit):
        LOGGER.debug(f'compile_parameter_list: index is {index}')
        LOGGER.debug(f'compiling a parameter list with token {tokens[index].tag , tokens[index].text}')
        parameter_list_unit = ET.SubElement(compilation_unit, 'parameterList')

        # sym  kw/id   id        sym kw/id id     sym sym
        # (    type    varName  ',' type  varName*  )

        while (not self.is_closing_paren(tokens[index])):
            if (self.is_keyword(tokens[index])):
                index = self.compile_keyword(tokens, index, parameter_list_unit)
            elif (self.is_identifier(tokens[index])):
                index = self.compile_identifier(tokens, index, parameter_list_unit)
            else:
                raise JackParseError(f'expected a keyword/identifier after opening a parmeter list but found {tokens[index].tag , tokens[index].text}')

            index = self.compile_identifier(tokens, index, parameter_list_unit)

            if (self.is_comma(tokens[index])):
                index = self.compile_symbol(tokens, index, parameter_list_unit)

        return index


    def compile_subroutine_body(self, tokens, index, compilation_unit):
        LOGGER.debug(f'compile_subroutine_body: index is {index}')
        LOGGER.debug(f'compiling a subroutine body with token {tokens[index].tag , tokens[index].text}')
        subroutine_unit = ET.SubElement(compilation_unit, 'subroutineBody')


        # { varDec statements }
        index = self.compile_symbol(tokens, index, subroutine_unit)
        index = self.compile_var_def(tokens, index, subroutine_unit)
        index = self.compile_statements(tokens, index, subroutine_unit)
        index = self.compile_symbol(tokens, index, subroutine_unit)

        return index


    def compile_var_def(self, tokens, index, compilation_unit):
        if not (self.is_var(tokens[index])):
            LOGGER.debug(f'compile_var_def: no variables found at index {index} token {tokens[index].tag , tokens[index].text}')
            return index


    def compile_statements(self, tokens, index, compilation_unit):
        if (not self.is_statement(tokens[index])):
            LOGGER.debug('compile_statements: no statements found at index {index} token {tokens[index].tag , tokens[index].text}')
            return index


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
