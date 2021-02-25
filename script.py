import urllib.request
import json
import zipfile
import psycopg2
import xmlschema
from pprint import pprint
import re
import os
"""
with urllib.request.urlopen(r'http://fias.nalog.ru/WebServices/Public/GetLastDownloadFileInfo') as response:
    versions = json.loads(response.read())
GarXMLFullURL = versions["GarXMLFullURL"]
url = urllib.request.urlretrieve('https://fias.nalog.ru/DownloadUpdates?file=gar_xml.zip&version=20200922', os.getcwd() + r'\gar_xml.zip')

gar_zip = zipfile.ZipFile('/mnt/bad63750-d3a5-46f9-9477-a5075147cae2/fias/fias/gar_xml.zip')
for file in gar_zip.namelist():
    if file.find('/') != -1:
        if file.split('/')[0] == '30' or file.split('/')[0] == 'Schemas':
            gar_zip.extract(file, os.getcwd())
    else:
        gar_zip.extract(file, os.getcwd())
"""
try:
    #conn = psycopg2.connect("dbname=geodata user=postgres password=07071907 host=172.17.13.6")
    conn = psycopg2.connect("dbname=geodata user=postgres password=07071907 host=localhost")
except psycopg2.Error as e:
    print(e)
cursor = conn.cursor()

cursor.execute("CREATE SCHEMA IF NOT EXISTS fiastest;")

conn.commit()



def parseXsd(directory):
    """
    Парсинг XSD файлов

    Принимает на вход папку с XSD файлами, разбирает их по очереди
    и на выходе выдает словарь вида:

    '<ИМЯ ФАЙЛА СХЕМЫ И СООТВЕТСТВУЮЩЕГО ЕЙ XML>': {
        'tableName': <ИМЯ ТАБЛИЦЫ>,
        'fields': {
            <ИМЯ ПОЛЯ>: {
                'name': '<ИМЯ ПОЛЯ>',
                'type': '<ТИП ПОЛЯ>,
                'length': '<ДЛИНА ПОЛЯ>' (опционально)
            },
            ...
        },
        'object': <объект XMLschema>
    }
    """
    parsedXSD = {}
    #for xsd in os.listdir(directory.replace('\\', '\\\\')):
    for xsd in os.listdir(directory):
        #schema = open(directory.replace('\\', '\\\\') + '\\\\' + xsd, 'r', encoding='utf_8_sig')
        schema = open(directory + '/' + xsd, 'r', encoding='utf_8_sig')
        schemadict = {}
        schemadict['object'] = xmlschema.XMLSchema(directory + '/' + xsd)
        schemastr = schema.read()

        def extractContent(xsd):
            """
            Извлекает полезное содержимое из XSD файла

            Отбрасывает преамбулу, убирает все переносы строк и табуляции
            """
            string = xsd.replace('\n','').replace('\t','')
            return string[string.find('<xs:', 0):]

        openTags = []
        def diver(string, dictionary, filename, openTags=openTags):
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
                    tempDict['name'] = openTagNameWithAttributes[openTagNameWithAttributes.find(' name=')+7:openTagNameWithAttributes.find('"',openTagNameWithAttributes.find(' name=')+8)]
                    dictionary['fields'].append(tempDict)
                
                if openTagNameClear == 'restriction':
                    if openTagNameWithAttributes[openTagNameWithAttributes.find(' base=')+10:openTagNameWithAttributes.find('"',openTagNameWithAttributes.find(' base=')+8)] == 'string':
                         dictionary['fields'][-1]['type'] = 'character varying'
                    elif openTagNameWithAttributes[openTagNameWithAttributes.find(' base=')+10:openTagNameWithAttributes.find('"',openTagNameWithAttributes.find(' base=')+8)] == 'integer' or openTagNameWithAttributes[openTagNameWithAttributes.find(' base=')+10:openTagNameWithAttributes.find('"',openTagNameWithAttributes.find(' base=')+8)] == 'int':
                         dictionary['fields'][-1]['type'] = 'bigint'
                    else:
                        dictionary['fields'][-1]['type'] = openTagNameWithAttributes[openTagNameWithAttributes.find(' base=')+10:openTagNameWithAttributes.find('"',openTagNameWithAttributes.find(' base=')+8)]

                if openTagNameClear == 'totalDigits' or openTagNameClear == 'length' or openTagNameClear == 'maxLength':
                    dictionary['fields'][-1]['length'] = int(openTagNameWithAttributes[openTagNameWithAttributes.find(' value=')+8:openTagNameWithAttributes.find('"',openTagNameWithAttributes.find(' value=')+8)])

                if openTagNameWithAttributes.find('type') != -1:
                    dictionary['fields'][-1]['type'] = openTagNameWithAttributes[openTagNameWithAttributes.find(' type=')+10:openTagNameWithAttributes.find('"',openTagNameWithAttributes.find(' type=')+8)]

                if openTagNameWithAttributes[-2] == '/':
                    openTags.pop()
                diver(string[openTagStartIndex+len(openTagNameWithAttributes):],dictionary,filename)
            else:
                openTags.pop()
                closeTagStartIndex = string.find('</xs:')
                closeTagName = string[closeTagStartIndex:string.find('>')+1]
                diver(string[closeTagStartIndex+len(closeTagName):],dictionary,filename)


        string = extractContent(schemastr)
        diver(string, schemadict, xsd)
        for field in schemadict['fields']:
            if 'type' not in field or field['type'] == 'integer' or field['type'] == 'int':
                field['type'] = 'bigint'
        
        

        parsedXSD[xsd[3:xsd.find('_2')]] = schemadict
        

        schema.close()
    return parsedXSD


#parsedXSD = parseXsd(os.getcwd() + '\Schemas')
parsedXSD = parseXsd(os.getcwd() + '/Schemas')
def createPgTables(directory, parsedXSD, conn, cursor):
    """
    Создание таблиц в БД PostgreSQL

    Функция принимает директорию с XML, массив разобранных XSD файлов, конвертированных в словари,
    объект соединения с БД и объект курсора.
    Создает из каждого XSD отдельную таблицу в БД.
    """
    for item in os.listdir(directory):
        if item.find('.XML') != -1:
            if item[3:item.find('_2')] in list(parsedXSD.keys()):
                cursor.execute("CREATE TABLE IF NOT EXISTS fiastest.{0} ({1} bigint CONSTRAINT {0}_{1}_pk PRIMARY KEY);".format(item[3:item.find('_2')], parsedXSD[item[3:item.find('_2')]]['fields'][0]['name'].lower()))
                
                conn.commit()
                for field in parsedXSD[item[3:item.find('_2')]]['fields'][1:]:
                    if field['type'] == 'character varying':
                        cursor.execute("ALTER TABLE fiastest.{0} ADD COLUMN \"{1}\" {2}({3});".format(item[3:item.find('_2')], field['name'].lower(), field['type'], field['length']))
                    if field['type'] == 'date' or field['type'] == 'boolean' or field['type'] == 'bigint':
                        cursor.execute("ALTER TABLE fiastest.{0} ADD COLUMN \"{1}\" {2};".format(item[3:item.find('_2')], field['name'].lower(), field['type']))
                
            if item.find('PARAMS_2') != -1:
                cursor.execute("CREATE TABLE IF NOT EXISTS fiastest.{0} ({1} bigint CONSTRAINT {0}_{1}_pk PRIMARY KEY);".format(item[3:item.find('_2')], parsedXSD['PARAM']['fields'][0]['name'].lower()))
                conn.commit()
                for field in parsedXSD['PARAM']['fields'][1:]:
                    if field['type'] == 'character varying':
                        cursor.execute("ALTER TABLE fiastest.{0} ADD COLUMN \"{1}\" {2}({3});".format(item[3:item.find('_2')], field['name'].lower(), field['type'], field['length']))
                    if field['type'] == 'date' or field['type'] == 'boolean' or field['type'] == 'bigint':
                        cursor.execute("ALTER TABLE fiastest.{0} ADD COLUMN \"{1}\" {2};".format(item[3:item.find('_2')], field['name'].lower(), field['type']))
        if item == '30':
            #createPgTables(directory + '\\' + item, parsedXSD, conn, cursor)
            createPgTables(directory + '/' + item, parsedXSD, conn, cursor)
            
        conn.commit()

createPgTables(os.getcwd(), parsedXSD, conn, cursor)

def fillPgTables(directory, parsedXSD, cursor, conn):
    
    for item in os.listdir(directory):
        
        if item.find('.XML') != -1:
            if item[3:item.find('_2')] in list(parsedXSD.keys()):
                #data = parsedXSD[item[3:item.find('_2')]]['object'].to_dict(directory + '\\' + item)
                data = parsedXSD[item[3:item.find('_2')]]['object'].to_dict(directory + '/' + item)
                
                if data != None:
                    for line in data[list(data.keys())[0]]:
                        columns = ''
                        values = ''
                        for key in line:
                            columns = columns + '"' + str(key[1:]).lower() + '", '
                            values = values + '\'' + str(line[key]) + '\', '
                        print("INSERT INTO fiastest.{0} ({1}) VALUES ({2});".format(item[3:item.find('_2')].lower(), columns[:-2], values[:-2]))
                        cursor.execute("INSERT INTO fiastest.{0} ({1}) VALUES ({2});".format(item[3:item.find('_2')].lower(), columns[:-2], values[:-2]))
                    conn.commit()
                
            if item.find('PARAMS_2') != -1:
                #data = parsedXSD['PARAM']['object'].to_dict(directory + '\\' + item)
                data = parsedXSD['PARAM']['object'].to_dict(directory + '/' + item)
                if data != None:
                    for line in data[list(data.keys())[0]]:
                        columns = ''
                        values = ''
                        for key in line:
                            columns = columns + '"' + str(key[1:]).lower() + '", '
                            values = values + '\'' + str(line[key]) + '\', '
                        print("INSERT INTO fiastest.{0} ({1}) VALUES ({2});".format(item[3:item.find('_2')].lower(), columns[:-2], values[:-2]))
                        cursor.execute("INSERT INTO fiastest.{0} ({1}) VALUES ({2});".format(item[3:item.find('_2')].lower(), columns[:-2], values[:-2]))
                    conn.commit()
        
        
        if item == '30':
            #fillPgTables(directory + '\\' + item, parsedXSD, cursor, conn)
            fillPgTables(directory + '/' + item, parsedXSD, cursor, conn)

fillPgTables(os.getcwd(), parsedXSD, cursor, conn)

conn.close()