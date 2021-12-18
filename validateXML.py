import os
from lxml import etree

from findXSD import findXSD

from config import XSD_DIRECTORY, XML_DIRECTORY

def validate(xml_path: str, xsd_path: str) -> bool:
    xmlschema_doc = etree.parse(xsd_path)
    xmlschema = etree.XMLSchema(xmlschema_doc)

    xml_doc = etree.parse(xml_path)
    result = xmlschema.validate(xml_doc)

    xml_name = os.path.splitext(xml_path)[0].split('_2')[0]
    if result:
        print(xml_name + '   ---   Valid! :)')
    else:
        print(xml_name + '   ---   Not valid! :(')

    return result

for file in os.listdir(XML_DIRECTORY):
    if file.find('.XML') != -1:
        validate(os.path.join(XML_DIRECTORY, file), findXSD(XSD_DIRECTORY, file.split('_2')[0]))
    else:
        path = os.path.join(XML_DIRECTORY, file)
        for ifile in os.listdir(path):
            validate(os.path.join(path, ifile), findXSD(XSD_DIRECTORY, ifile.split('_2')[0]))