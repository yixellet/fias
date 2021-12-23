import os
from lxml import etree

def findXSD(dir_path: str, namepart: str) -> str:
    """
    Находит файл в директории и возвращает его полный путь
    """
    
    if namepart == 'AS_ADDHOUSE_TYPES':
        needle = 'AS_HOUSE_TYPES_2'
    elif namepart.find('_PARAMS') != -1:
        needle = 'AS_PARAM_2'
    else:
        needle = namepart + '_2'

    for file in os.listdir(dir_path):
        if file[:len(needle)] == needle:
            return os.path.join(dir_path, file)


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

    return {'File': xml_name, 'IsValid': result}


def batchValidation(xml_dir, xsd_dir, reg_code):
    """
    Пакетная валидация XML файлов.
    """

    result = []
    for file in os.listdir(xml_dir):
        if file.find('.XML') != -1:
            result.append(validate(os.path.join(xml_dir, file), findXSD(xsd_dir, file.split('_2')[0])))
        elif file == reg_code:
            path = os.path.join(xml_dir, file)
            for ifile in os.listdir(path):
                result.append(validate(os.path.join(path, ifile), findXSD(xsd_dir, ifile.split('_2')[0])))
    return result