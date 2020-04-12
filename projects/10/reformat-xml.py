#!/usr/local/bin/python3

import sys
import unittest
import xml.etree.ElementTree as ET
import os
from tempfile import TemporaryDirectory



def prettify_elements(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            prettify_elements(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def reformat_xml_to_standardize_whitespace(xml):
    tree = ET.fromstring(''.join(xml.split()))
    prettify_elements(tree)
    return ET.tostring(tree, encoding='unicode', short_empty_elements=False)


if __name__ == '__main__':
    filename = sys.argv[1]

    with open(filename, 'r') as f:
        xml = ''.join(f.readlines())
        print(reformat_xml_to_standardize_whitespace(xml))
