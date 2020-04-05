#!/usr/local/bin/python3

import xml.etree.ElementTree as ET


KEYWORDS = [
    'class', 'constructor', 'function',
    'method', 'field', 'static', 'var',
    'int', 'char', 'boolean', 'void', 'true',
    'false', 'null', 'this', 'let', 'do',
    'if', 'else' ,'while', 'return'
]

SYMBOLS = '{ } ( ) [ ] . - , ; + - * / & | < > = -'.split()


class Tokenizer:
    def tokenize(self, input):
        tokens = ET.Element('tokens')
        print('BEGIN PARSING')
        print(f'here is our input {input}')

        index = 0
        peekahead = None

        while (index < len(input)):
            if index == len(input) - 1:
                print('we are at the last element - no peeking')
                peekahead = None
            else:
                peekahead = input[index+1]

            x = input[index]

            print(f'index: {index}, x: {x}, peekahead: {peekahead}')

            if x == '/' and peekahead == '/':
                index = self.tokenize_single_line_comment(tokens, index+1, input)
            elif x == '/' and peekahead == '*':
                index = self.tokenize_multi_line_comment(tokens, index+1, input)
            elif x.isalpha():
                index = self.tokenize_keyword_or_identifier(tokens, index, input)
            elif x.isdigit():
                index = self.tokenize_integer_constant(tokens, index, input)
            elif x == '"':
                index = self.tokenize_string_constant(tokens, index+1, input)
            elif x in SYMBOLS:
                print('SYMBOL')
                ET.SubElement(tokens, 'symbol').text = x
                index += 1
            else:
                index += 1

        self.prettify_elements(tokens)
        return ET.tostring(tokens, encoding='unicode')


    def tokenize_single_line_comment(self, tokens, index, input):
        while (index < len(input)):
            if input[index] == '\n':
                print('reached the end of single-line comment')
                return index+1

            index += 1

        return index


    def tokenize_multi_line_comment(self, tokens, index, input):
        while (index < len(input)):
            if input[index-1] == '*' and input[index] == '/':
                print('reached the end of mult-line comment')
                return index+1

            index += 1

        return index


    def tokenize_keyword_or_identifier(self, tokens, index, input):
        current_token = ''

        while (index < len(input)):
            if not input[index].isalnum():
                if current_token in KEYWORDS:
                    print('KEYWORD')
                    ET.SubElement(tokens, 'keyword').text = current_token
                    return index
                else:
                    print('IDENTIFIER')
                    ET.SubElement(tokens, 'identifier').text = current_token
                    return index

            current_token += input[index]
            index += 1

        return index


    def tokenize_integer_constant(self, tokens, index, input):
        current_token = ''

        while (index < len(input)):
            if not input[index].isdigit():
                print('INTEGERCONSTANT')
                ET.SubElement(tokens, 'integerConstant').text = current_token
                return index

            current_token += input[index]
            index += 1

        return index


    def tokenize_string_constant(self, tokens, index, input):
        current_token = ''

        while (index < len(input)):
            if input[index] == '"':
                print('STRINGCONSTANT')
                ET.SubElement(tokens, 'stringConstant').text = current_token
                return index+1

            current_token += input[index]

            index += 1

        return index



    def tokenize__insane_way(self, input):
        tokens = ET.Element('tokens')

        print('BEGIN PARSING')
        print(f'here is our input {input}')
        current_token = ''
        startedID = False
        startedString = False
        startedSingleLineComment = False
        startedMultilineComment = False
        peekahead = None
        peekbehind = None

        for idx, x in enumerate(input):
            if idx > 1:
                peekbehind = input[idx-1]
            if idx == len(input) - 1:
                print('we are at the last element - no peeking')
                peekahead = None
            else:
                peekahead = input[idx+1]

            print(f'x: {x}, peekahead: {peekahead},  peekbehind: {peekbehind}')

            if x == '\n':
                print('is a newline')
                if startedSingleLineComment:
                    print('ending comment')
                    startedSingleLineComment = False
            elif x == '/' and peekbehind == '*' and startedMultilineComment:
                    print('our long national nightmare is over; ending multiline comment')
                    startedMultilineComment = False
            elif startedSingleLineComment or startedMultilineComment:
                print('still in a comment - ignoring input')
            elif x in SYMBOLS:
                if x == '/' and peekahead == '/':
                    print('starting comment and ignoring all input until we see a newline')
                    startedSingleLineComment = True
                    continue
                if x == '/' and peekahead == '*':
                    print('starting multiline comment and ignoring all input until we see the end')
                    startedMultilineComment = True
                    continue
                elif startedID:
                    if current_token.isdigit():
                        print('INTEGERCONSTANT')
                        ET.SubElement(tokens, 'integerConstant').text = current_token
                    elif current_token.isalnum():
                        print('IDENTIFIER')
                        ET.SubElement(tokens, 'identifier').text = current_token
                    startedID = False
                elif startedString:
                    print('STRINGCONSTANT')
                    ET.SubElement(tokens, 'stringConstant').text = current_token
                    startedString = False

                print('SYMBOL')
                ET.SubElement(tokens, 'symbol').text = x
                current_token = ''
            elif x.isalpha():
                startedID = True
                current_token += x
            elif x.isdigit():
                print('is a digit, starting an identifier')
                startedID = True
                current_token += x
            elif x == '"' and not startedString:
                print('is a quote, starting string')
                startedString = True
            elif x == '"' and startedString:
                print('STRINGCONSTANT')
                ET.SubElement(tokens, 'stringConstant').text = current_token
                startedString = False
                startedID = False
                current_token = ''
            elif x == ' ':
                print('got to end of token')
                if current_token in KEYWORDS:
                    print('KEYWORD')
                    ET.SubElement(tokens, 'keyword').text = current_token
                elif current_token.isdigit():
                    print('INTEGERCONSTANT')
                    ET.SubElement(tokens, 'integerConstant').text = current_token
                elif current_token.isalnum():
                    print('IDENTIFIER')
                    ET.SubElement(tokens, 'identifier').text = current_token
                current_token = ''

            else:
                print(f'adding onto current token')
                current_token += x

        self.prettify_elements(tokens)
        return ET.tostring(tokens, encoding='unicode')


    def prettify_elements(self, elem, level=0):
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.prettify_elements(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
