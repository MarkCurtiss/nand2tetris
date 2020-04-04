#!/usr/local/bin/python3

import xml.etree.ElementTree as ET


KEYWORDS = [
    'class', 'constructor', 'function',
    'method', 'field', 'static', 'var',
    'int', 'char', 'boolean', 'void', 'true',
    'false', 'null', 'this', 'let', 'do',
    'if', 'else' ,'while', 'return'
]

SYMBOLS = '{ } ( ) [ ] - , ; + - * / & | < > = -'.split()


class Tokenizer:
    def tokenize(self, input):
        tokens = ET.Element('tokens')

        print(f'here is our input {input}')
        current_token = ''
        startedID = False
        startedString = False
        startedComment = False

        for x in input:
            print(f'now examining: {x}')
            if x in SYMBOLS:
                if startedID:
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
            elif x == '\n':
                print('is a newline')
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
