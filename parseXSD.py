import os
import re

def extractContent(xsd):
    """
    Извлекает полезное содержимое из XSD файла
    Отбрасывает преамбулу, убирает все переносы строк и табуляции
    """
    string = xsd.replace('\n','').replace('\t','')
    return string[string.find('<xs:', 0):]

def diver(string, dictionary, filename, openTags):
    """
    Конвертирует XSD в словарь

    Принимает конвертированный в строку XSD, словарь, в который будут добавляться данные из XSD,
    имя xsd файла, вспомогательный массив, в который заносятся открытые теги. 
    """
    filename = filename
    if len(string) < 2:
        return 'Search complete'

    if string.find('<xs:') != -1 and string.find('</xs') != -1 and string.find('<xs:') < string.find('</xs'):
        openTagStartIndex = string.find('<xs:')
        openTagNameWithAttributes = string[openTagStartIndex:string.find('>')+1]
        openTagNameClear = openTagNameWithAttributes[4:re.search(r'\ |>', openTagNameWithAttributes).start()]
        openTags.append(openTagNameClear)

        if openTagNameClear == 'element' and openTagNameWithAttributes.find('maxOccurs') == -1:
            if openTagNameWithAttributes[openTagNameWithAttributes.find(' name=')+7:openTagNameWithAttributes.find('"',openTagNameWithAttributes.find(' name=')+8)] == 'ITEMS':
                dictionary['tableName'] = filename[3:filename.find('_2')]
            else:
                dictionary['tableName'] = openTagNameWithAttributes[openTagNameWithAttributes.find(' name=')+7:openTagNameWithAttributes.find('"',openTagNameWithAttributes.find(' name=')+8)]
            dictionary['fields'] = []

        if openTagNameClear == 'attribute':
            tempDict = {}
            tempDict['name'] = openTagNameWithAttributes[openTagNameWithAttributes.find(' name=')+7:openTagNameWithAttributes.find('"',openTagNameWithAttributes.find(' name=')+8)].lower()
            dictionary['fields'].append(tempDict)
        
        if openTagNameClear == 'restriction':
            if openTagNameWithAttributes[openTagNameWithAttributes.find(' base=')+10:openTagNameWithAttributes.find('"',openTagNameWithAttributes.find(' base=')+8)] == 'string':
                    dictionary['fields'][-1]['type'] = 'character varying'
            elif openTagNameWithAttributes[openTagNameWithAttributes.find(' base=')+10:openTagNameWithAttributes.find('"',openTagNameWithAttributes.find(' base=')+8)] == 'integer' or openTagNameWithAttributes[openTagNameWithAttributes.find(' base=')+10:openTagNameWithAttributes.find('"',openTagNameWithAttributes.find(' base=')+8)] == 'int':
                    dictionary['fields'][-1]['type'] = 'integer'
            else:
                dictionary['fields'][-1]['type'] = openTagNameWithAttributes[openTagNameWithAttributes.find(' base=')+10:openTagNameWithAttributes.find('"',openTagNameWithAttributes.find(' base=')+8)]

        if openTagNameClear == 'totalDigits' or openTagNameClear == 'length' or openTagNameClear == 'maxLength':
            dictionary['fields'][-1]['length'] = int(openTagNameWithAttributes[openTagNameWithAttributes.find(' value=')+8:openTagNameWithAttributes.find('"',openTagNameWithAttributes.find(' value=')+8)])

        if openTagNameWithAttributes.find('type') != -1:
            dictionary['fields'][-1]['type'] = openTagNameWithAttributes[openTagNameWithAttributes.find(' type=')+10:openTagNameWithAttributes.find('"',openTagNameWithAttributes.find(' type=')+8)]

        if openTagNameWithAttributes[-2] == '/':
            openTags.pop()
        diver(string[openTagStartIndex+len(openTagNameWithAttributes):],dictionary,filename, openTags)
    else:
        openTags.pop()
        closeTagStartIndex = string.find('</xs:')
        closeTagName = string[closeTagStartIndex:string.find('>')+1]
        diver(string[closeTagStartIndex+len(closeTagName):],dictionary,filename, openTags)

def parseXsd(directory):
    """
    Парсинг XSD файлов

    Принимает на вход папку с XSD файлами, разбирает их по очереди
    и на выходе выдает словарь
    """
    parsedXSD = []
    for xsd in os.listdir(directory):
        schema = open(os.path.join(directory, xsd), 'r', encoding='utf_8_sig')
        schemadict = {}
        schemadict['fileName'] = xsd
        schemastr = schema.read()
        string = extractContent(schemastr)

        openTags = []
        diver(string, schemadict, xsd, openTags)
        for field in schemadict['fields']:
            if field['type'] == 'int':
                field['type'] = 'integer'
            if field['type'] == 'long':
                field['type'] = 'bigint'

        parsedXSD.append(schemadict)
        
        schema.close()
    print('--- XSD схемы обработаны. Общее количество схем - {count} ---'.format(count=len(parsedXSD)))
    return parsedXSD
