from lxml import etree, objectify

from config import XSD_DIRECTORY, XML_DIRECTORY

def parseXSD_2(xsdFile):
    with open(xsdFile) as file:
        xsd = file.read()
    
    root = objectify.fromstring(xsd)

    attrib = root.attrib
    print(attrib)

if __name__ == "__main__":
    import os
    file = os.path.join(XML_DIRECTORY, 'AS_ADDHOUSE_TYPES_20211216_7d286806-4185-4d17-9f71-3b7ceb0bcab7.XML')
    parseXSD_2(file)