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
LOGGER.setLevel(logging.INFO)


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
            LOGGER.debug(f'index: {index}, token: {token.tag , token.text}, peekahead: {peekahead.tag , peekahead.text}')

            # main parse loop
            if self.is_class(token):
                LOGGER.debug('found a class')
                index = self.compile_class(tokens, index, compilation_unit)

            # . . .


            index += 1

        self.prettify_elements(compilation_unit)
        return ET.tostring(compilation_unit, encoding='unicode', short_empty_elements=False)


    def is_first_class(self, index):
        return index == 0


    def is_class(self, token):
        LOGGER.debug(f'is_class called with tag {token.tag} and text {token.text}')
        return token.tag == 'keyword' and token.text == 'class'


    def is_symbol(self, token):
        return token.tag == 'symbol'


    def is_operation(self, token):
        return token.tag == 'symbol' and token.text in '+-*/&|<>='


    def is_unary_op(self, token):
        return token.tag == 'symbol' and token.text in '-~'


    def is_identifier(self, token):
        return token.tag == 'identifier'


    def is_keyword(self, token):
        return token.tag == 'keyword'


    def is_comma(self, token):
        return token.tag == 'symbol' and token.text == ','


    def is_closing_paren(self, token):
        return token.tag == 'symbol' and token.text == ')'


    def is_symbol_type(self, token, symbol_type):
        return token.tag == 'symbol' and token.text == symbol_type


    def is_class_var(self, token):
        return self.is_keyword(token) and token.text in ['static', 'field']


    def is_statement(self, token):
        return self.is_keyword(token) and token.text in ['let' ,'if', 'while', 'do', 'return']


    def is_statement_type(self, token, statement_type):
        return self.is_keyword(token) and token.text == statement_type


    def is_let_statement(self, token):
        return self.is_statement_type(token, 'let')


    def is_if_statement(self, token):
        return self.is_statement_type(token, 'if')


    def is_while_statement(self, token):
        return self.is_statement_type(token, 'while')


    def is_do_statement(self, token):
        return self.is_statement_type(token, 'do')


    def is_return_statement(self, token):
        return self.is_statement_type(token, 'return')


    def is_subroutine_declaration(self, token):
        return self.is_keyword(token) and token.text in ['function', 'constructor', 'method']


    def is_var(self, token):
        return self.is_keyword(token) and token.text == 'var'


    def is_integer_constant(self, token):
        return token.tag == 'integerConstant'


    def is_string_constant(self, token):
        return token.tag == 'stringConstant'


    def log_state(self, method, index, tokens):
        LOGGER.debug(f'{method}: we are at index {index} (file line {index+2}) and looking at {tokens[index].tag , tokens[index].text}')


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


    def compile_keyword(self,  tokens, index, compilation_unit, expected=None):
        current_token = tokens[index]

        if (expected and current_token.text != expected):
            raise JackParseError(f'compile_keyword called and expected {expected} but got {current_token.text}')

        ET.SubElement(compilation_unit, 'keyword').text = current_token.text
        return index+1

            # index = self.simple_compile(current_token, index, 'integerConstant', compilation_unit)


    def simple_compile(self, token, index, tag, compilation_unit):
        LOGGER.debug(f'simple_compile called with token {token.text} and index {index} and compilation_unit {compilation_unit}')
        ET.SubElement(compilation_unit, tag).text = token.text
        return index+1


    def compile_symbol(self, tokens, index, compilation_unit, expected=None):
        current_token = tokens[index]
        if (not self.is_symbol(current_token)):
            raise JackParseError(f'compile_symbol called on a non-symbol! {tokens[index].tag, tokens[index].text}')

        if (expected and current_token.text != expected):
            raise JackParseError(f'compile_symbol called and expected {expected} but got {tokens[index].text}')

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
        while (self.is_var(tokens[index])):
            index = self.compile_var_def(tokens, index, subroutine_unit)
        index = self.compile_statements(tokens, index, subroutine_unit)
        self.log_state('compile_subroutine_body', index, tokens)
        index = self.compile_symbol(tokens, index, subroutine_unit)

        return index


    def compile_var_def(self, tokens, index, compilation_unit):
        if not (self.is_var(tokens[index])):
            LOGGER.debug(f'compile_var_def: no variables found at index {index} token {tokens[index].tag , tokens[index].text}')
            return index

        LOGGER.debug(f'compile_var_def: found some variable definitions at index {index} token {tokens[index].tag , tokens[index].text}')
        var_unit = ET.SubElement(compilation_unit, 'varDec')
        # var
        index = self.compile_keyword(tokens, index, var_unit)

        # type
        if (self.is_identifier(tokens[index])):
            index = self.compile_identifier(tokens, index, var_unit)
        elif (self.is_keyword(tokens[index])):
            index = self.compile_keyword(tokens, index, var_unit)
        else:
            raise JackParseError(f'keyword or identifier expected in variable definition at index {index}, found {tokens[index].tag , tokens[index].text}')

        # identifier
        index = self.compile_identifier(tokens, index, var_unit)

        while (self.is_comma(tokens[index])):
            index = self.compile_symbol(tokens, index, var_unit)
            LOGGER.debug(f'compile_var_def: after compiling a , index is {index}')
            index = self.compile_identifier(tokens, index, var_unit)
            LOGGER.debug(f'compile_var_def: after compiling a variable name index is {index} {tokens[index].tag , tokens[index].text}')

        # ;
        index = self.compile_symbol(tokens, index, var_unit)

        return index

    def compile_statements(self, tokens, index, compilation_unit):
        statements_unit = ET.SubElement(compilation_unit, 'statements')
        LOGGER.debug(f'compile_statements {index} {tokens[index].tag , tokens[index].text}')
        current_token = tokens[index]
        if (not self.is_statement(current_token)):
            return index

        while(self.is_statement(tokens[index])):
            if (self.is_let_statement(tokens[index])):
                self.log_state('compile_statements - is let ', index, tokens)
                index = self.compile_let_statement(tokens, index, statements_unit)
            elif (self.is_if_statement(tokens[index])):
                self.log_state('compile_statements - is if', index, tokens)
                index = self.compile_if_statement(tokens, index, statements_unit)
            elif (self.is_while_statement(tokens[index])):
                self.log_state('compile_statements - is while', index, tokens)
                index = self.compile_while_statement(tokens, index, statements_unit)
            elif (self.is_do_statement(tokens[index])):
                self.log_state('compile_statements - is do', index, tokens)
                index = self.compile_do_statement(tokens, index, statements_unit)
            elif (self.is_return_statement(tokens[index])):
                self.log_state('compile_statements - is return', index, tokens)
                index = self.compile_return_statement(tokens, index, statements_unit)
            else:
                raise JackParseError('compile_statements found an unexpected statement type {tokens[index].tag , tokens[index].text}')


        return index


    def compile_let_statement(self, tokens, index, compilation_unit):
        let_unit = ET.SubElement(compilation_unit, 'letStatement')

        self.log_state('compile_let_statement', index, tokens)
        next_five_tokens = [ x.text for x in [ tokens[index], tokens[index+1], tokens[index+2], tokens[index+3], tokens[index+4] ] ]
        LOGGER.debug(f'in compile_let statements, the next 5 tokens are {next_five_tokens}')

        if (not self.is_let_statement(tokens[index])):
            raise JackParseError(f'compile_let_statement called on a non-let statement {tokens[index].tag , tokens[index].text}')

	#let length = Keyboard.readInt("HOW MANY NUMBERS? ");
        #let a[i] = Keyboard.readInt("ENTER THE NEXT NUMBER: ");
        # let
        index = self.compile_keyword(tokens, index, let_unit)
        # identifier
        index = self.compile_identifier(tokens, index, let_unit)

        # '[' expression ']' }
        if (self.is_symbol_type(tokens[index], '[')):
            self.log_state('compile_let_statement ; [expression] branch', index, tokens)
            index = self.compile_symbol(tokens, index, let_unit, expected='[')
            index = self.compile_expression(tokens, index, let_unit)
            index = self.compile_symbol(tokens, index, let_unit, expected=']')


        index = self.compile_symbol(tokens, index, let_unit, expected='=')
        # expression
        LOGGER.debug(f'compile_let_statement; about to compile an expression at index {index}: {tokens[index].text}')
        index = self.compile_expression(tokens, index, let_unit)
        LOGGER.debug(f'compile_let_statement; done compiling expression and now looking for ;. current token is {tokens[index].text} and last token was {tokens[index-1].text}')
        # ;
        index = self.compile_symbol(tokens, index, let_unit)

        return index

    def compile_while_statement(self, tokens, index, compilation_unit):
        while_unit = ET.SubElement(compilation_unit, 'whileStatement')

        index = self.compile_keyword(tokens, index, while_unit, expected='while')
        index = self.compile_symbol(tokens, index, while_unit, expected='(')
        index = self.compile_expression(tokens, index, while_unit)
        index = self.compile_symbol(tokens, index, while_unit, expected=')')
        index = self.compile_symbol(tokens, index, while_unit, expected='{')
        index = self.compile_statements(tokens, index, while_unit)
        index = self.compile_symbol(tokens, index, while_unit, expected='}')

        return index


    def compile_subroutine_call(self, tokens, index, compilation_unit, already_seen_identifier=False):
        if not already_seen_identifier:
            index = self.compile_identifier(tokens, index, compilation_unit)

        # we could be calling a standalone routine or a method; in the latter case we'll see a .
        if (self.is_symbol_type(tokens[index], '.')):
            index = self.compile_symbol(tokens, index, compilation_unit, expected='.')
            index = self.compile_identifier(tokens, index, compilation_unit)

        # (
        index = self.compile_symbol(tokens, index, compilation_unit, expected='(')
        # ??
        index = self.compile_expression_list(tokens, index, compilation_unit)
        # )
        index = self.compile_symbol(tokens, index, compilation_unit, expected=')')

        return index


    def compile_do_statement(self, tokens, index, compilation_unit):
        do_unit = ET.SubElement(compilation_unit, 'doStatement')

        # do subroutineName '( expressionList') ;
        # OR
        # do (className | varName) . subroutineName '(' expressionList ')';


        # do
        self.log_state('compile_do_statement', index, tokens)
        index = self.compile_keyword(tokens, index, do_unit)
        # subroutineName OR className OR varName
        self.log_state('compile_do_statement', index, tokens)
        index = self.compile_subroutine_call(tokens, index, do_unit)
        index = self.compile_symbol(tokens, index, do_unit, expected=';')

        return index


    def compile_return_statement(self, tokens, index, compilation_unit):
         # 'return' expression? ;
        return_unit = ET.SubElement(compilation_unit, 'returnStatement')

        index = self.compile_keyword(tokens, index, return_unit, expected='return')
        if (not self.is_symbol_type(tokens[index], ';')):
            index = self.compile_expression(tokens, index, return_unit)

        index = self.compile_symbol(tokens, index, return_unit, expected=';')

        return index

    def compile_if_statement(self, tokens, index, compilation_unit):
        # 'if' '(' expression ')' '{' statements '}'
        #( 'else'  '{' statements '}' )?

        if_unit = ET.SubElement(compilation_unit, 'ifStatement')
        self.log_state('compile_if_statement', index, tokens)
        index = self.compile_keyword(tokens, index, if_unit, expected='if')
        self.log_state('compile_if_statement', index, tokens)
        index = self.compile_symbol(tokens, index, if_unit, expected='(')
        self.log_state('compile_if_statement', index, tokens)
        index = self.compile_expression(tokens, index, if_unit)
        self.log_state('compile_if_statement', index, tokens)
        index = self.compile_symbol(tokens, index, if_unit, expected=')')
        self.log_state('compile_if_statement', index, tokens)
        index = self.compile_symbol(tokens, index, if_unit, expected='{')
        self.log_state('compile_if_statement', index, tokens)
        index = self.compile_statements(tokens, index, if_unit)
        self.log_state('compile_if_statement', index, tokens)
        index = self.compile_symbol(tokens, index, if_unit, expected='}')


        if (self.is_statement_type(tokens[index], 'else')):
            self.log_state('compile_if_statement - else branch', index, tokens)
            index = self.compile_keyword(tokens, index, if_unit, expected='else')
            self.log_state('compile_if_statement - else branch', index, tokens)
            index = self.compile_symbol(tokens, index, if_unit, expected='{')
            self.log_state('compile_if_statement - else branch', index, tokens)
            index = self.compile_statements(tokens, index, if_unit)
            self.log_state('compile_if_statement - else branch', index, tokens)
            index = self.compile_symbol(tokens, index, if_unit, expected='}')
            self.log_state('compile_if_statement - else branch', index, tokens)

        return index


    def compile_expression_list(self, tokens, index, compilation_unit):
        self.log_state('compile_expression_list', index, tokens)
        expression_list_unit = ET.SubElement(compilation_unit, 'expressionList')

        # expression lists always occur inside of () and can be empty
        # it's easier for us to tell here that we don't have any expressions rather than inside compile_expression
        if self.is_closing_paren(tokens[index]):
            return index

        index = self.compile_expression(tokens, index, expression_list_unit)
        while(self.is_comma(tokens[index])):
            index = self.compile_symbol(tokens, index, expression_list_unit, expected=',')
            index = self.compile_expression(tokens, index, expression_list_unit)

        return index



    def compile_expression(self, tokens, index, compilation_unit):
        self.log_state('compile_expression', index, tokens)
        expression_unit = ET.SubElement(compilation_unit, 'expression')

        # next_five_tokens = [ x.text for x in [ tokens[index], tokens[index+1], tokens[index+2], tokens[index+3], tokens[index+4] ] ]
        # LOGGER.debug(f'in compile_expression a {index}, the next 7 tokens are {next_five_tokens}')

        index = self.compile_term(tokens, index, expression_unit)
        # next_five_tokens = [ x.text for x in [ tokens[index], tokens[index+1], tokens[index+2], tokens[index+3], tokens[index+4] ] ]
        # LOGGER.debug(f'in compile_expression at {index}, we just compiled a term and the next 5 tokens are {next_five_tokens}')
        while (self.is_operation(tokens[index])):
            LOGGER.debug(f'in compile_expression at {index} we found an operationr {tokens[index].text}')
            index = self.compile_symbol(tokens, index, expression_unit)
            index = self.compile_term(tokens, index, expression_unit)

        LOGGER.debug(f'compile_expression - done compiling expression, now at token {tokens[index].text}')
        return index


    def compile_term(self, tokens, index, compilation_unit):
        term_unit = ET.SubElement(compilation_unit, 'term')
        current_token = tokens[index]

        # next_five_tokens = [ x.text for x in [ tokens[index], tokens[index+1], tokens[index+2], tokens[index+3], tokens[index+4] ] ]
        # LOGGER.debug(f'in compile_term, the next 5 tokens are {next_five_tokens}')

        # integer | string | keyword | varName | varName [ expression ] | subroutineCall | ( expression ) | unaryOpTerm
        if (self.is_integer_constant(tokens[index])):
            self.log_state('compile_term', index, tokens)
            index = self.simple_compile(tokens[index], index, 'integerConstant', term_unit)
        elif (self.is_string_constant(tokens[index])):
            index = self.simple_compile(tokens[index], index, 'stringConstant', term_unit)
        elif (self.is_keyword(tokens[index])):
            index = self.compile_keyword(tokens, index, term_unit)
        elif (self.is_identifier(tokens[index])):
            # if we're at an identifier we could be looking at
            # varName
            # varName[expression]
            # subroutineCall
            if tokens[index+1].text == '[':
                index = self.compile_identifier(tokens, index, term_unit)
                index = self.compile_symbol(tokens, index, term_unit, expected='[')
                index = self.compile_expression(tokens, index, term_unit)
                index = self.compile_symbol(tokens, index, term_unit, expected=']')
            elif tokens[index+1].text in '(.':
                index = self.compile_subroutine_call(tokens, index, term_unit)
            else:
                index = self.compile_identifier(tokens, index, term_unit)
        elif self.is_symbol_type(tokens[index], '('):
              index = self.compile_symbol(tokens, index, term_unit, expected='(')
              index = self.compile_expression(tokens, index, term_unit)
              index = self.compile_symbol(tokens, index, term_unit, expected=')')
        elif self.is_unary_op(tokens[index]):
              index = self.compile_symbol(tokens, index, term_unit)
              index = self.compile_term(tokens, index, term_unit)
        else:
            raise JackParseError(f'compile_term called on an unexpected token {tokens[index].text}')

        return index


    def prettify_elements(self, tree):
        return self.tokenizer.prettify_elements(tree)


if __name__ == '__main__':
    filename = sys.argv[1]

    compiler = CompilationEngine()
    LOGGER.debug(f'now tokenizing file: {filename}')
    # to use against a Jack file
    # diff -w <(./compilation_engine.py Square/Square.jack ) <(cat Square/SquareT.xml)
    with open(filename, 'r') as f:
        output = compiler.compile(''.join(f.readlines()))
        print(f'{output}')
