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

        for x in ' '.join(input.split()):
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
                startedID = True
                current_token += x
            elif x == '"' and not startedString:
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


        return ET.tostring(tokens, encoding="unicode")
