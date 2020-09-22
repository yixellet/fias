import urllib.request
import zipfile
import psycopg2
import xmlschema
from pprint import pprint
import re
import os

"""
with urllib.request.urlopen('http://fias.nalog.ru/WebServices/Public/GetLastDownloadFileInfo') as response:
    versions = json.loads(response.read())
GarXMLFullURL = versions["GarXMLFullURL"]
url = urllib.request.urlretrieve(GarXMLFullURL, os.getcwd() + '\gar_xml.zip')

gar_zip = zipfile.ZipFile('D:\\fias_gar_15092020\\gar_delta_xml.zip')
for file in gar_zip.namelist():
    if file.find('/') != -1:
        if file.split('/')[0] == '30' or file.split('/')[0] == 'Schemas':
            gar_zip.extract(file, 'D:\\fias_gar_15092020\\gar_delta')
    else:
        gar_zip.extract(file, 'D:\\fias_gar_15092020\\gar_delta')

"""

try:
    #conn = psycopg2.connect("dbname=geodata user=postgres password=07071907 host=172.17.13.6")
    conn = psycopg2.connect("dbname=geodata user=postgres password=07071907 host=localhost")
except psycopg2.Error as e:
    print(e)
cursor = conn.cursor()

"""
cursor.execute("CREATE SCHEMA IF NOT EXISTS fiastest;")

conn.commit()



def parseXsd(directory):
    parsedXSD = []
    #for xsd in os.listdir(directory.replace('\\', '\\\\')):
    for xsd in os.listdir(directory):
        #schema = open(directory.replace('\\', '\\\\') + '\\\\' + xsd, 'r', encoding='utf_8_sig')
        schema = open(directory + '/' + xsd, 'r', encoding='utf_8_sig')
        schemadict = {}
        schemastr = schema.read()

        def extractContent(xsd):
            string = xsd.replace('\n','').replace('\t','')
            return string[string.find('<xs:', 0):]

        openTags = []
        def diver(string, dictionary, filename, openTags=openTags):
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
            if 'type' not in field:
                field['type'] = 'bigint'
        parsedXSD.append(schemadict)

        schema.close()
    return parsedXSD


#parsedXSD = parseXsd('D:\\fias_gar_15092020\\gar_delta\\Schemas')
parsedXSD = parseXsd('/mnt/bad63750-d3a5-46f9-9477-a5075147cae2/fias/gar_delta/Schemas')
def createPgTables(parsedxsd, conn, cursor):
    for scheme in parsedxsd:
        cursor.execute("CREATE TABLE IF NOT EXISTS fiastest.{0} ({1} bigint CONSTRAINT {0}_{1}_pk PRIMARY KEY);".format(scheme['tableName'], scheme['fields'][0]['name']))
        conn.commit()
        for field in scheme['fields'][1:]:
            if field['type'] == 'character varying':
                cursor.execute("ALTER TABLE fiastest.{0} ADD COLUMN \"{1}\" {2}({3});".format(scheme['tableName'], field['name'], field['type'], field['length']))
            if field['type'] == 'date' or field['type'] == 'boolean' or field['type'] == 'bigint':
                cursor.execute("ALTER TABLE fiastest.{0} ADD COLUMN \"{1}\" {2};".format(scheme['tableName'], field['name'], field['type']))
            
            
            
        conn.commit()
createPgTables(parsedXSD, conn, cursor)
"""

def createSchemaList(directory):
    schemaList = []
    for xsd in os.listdir(directory):
        schemaList.append(xmlschema.XMLSchema(directory + '/' + xsd))
    return schemaList

schemaList = createSchemaList('/mnt/bad63750-d3a5-46f9-9477-a5075147cae2/fias/gar_delta/Schemas')
dic = schemaList[0].to_dict('/mnt/bad63750-d3a5-46f9-9477-a5075147cae2/fias/gar_delta/AS_ROOM_TYPES_20200914_d1ec5fa2-ba37-41be-9fe5-10ef35cc1932.XML')

pprint(dic)

conn.close()