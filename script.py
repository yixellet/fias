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
    conn = psycopg2.connect("dbname=geodata user=postgres password=07071907 host=172.17.13.6")
except psycopg2.Error as e:
    print(e)
cursor = conn.cursor()
cursor.execute("CREATE SCHEMA fiastest;")

conn.commit()



def parseXsd(directory):
    parsedXSD = []
    for xsd in os.listdir(directory.replace('\\', '\\\\')):
        schema = open(directory.replace('\\', '\\\\') + '\\\\' + xsd, 'r', encoding='utf_8_sig')
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
                         dictionary['fields'][-1]['type'] = 'varchar'
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
        parsedXSD.append(schemadict)

        schema.close()
    return parsedXSD


parsedXSD = parseXsd('D:\\fias_gar_15092020\\gar_delta\\Schemas')

def createPgTables(parsedxsd, conn, cursor):
    for scheme in parsedXSD:
        print(scheme['tableName'])
        cursor.execute("CREATE TABLE '{0}';".format(scheme['tableName']))
        conn.commit()
        for field in scheme['fields']:
            fieldType = ''
            if field['type'] == 'integer':
                fieldType = 'bigint'
            if field['type'] == 'string':
                fieldType = 'varchar{0}'.format(field['length'])
            if field['type'] == 'date':
                fieldType = 'date'

            cursor.execute("ALTER TABLE '{0}' ADD COLUMN '{1}' '{2}';".format(scheme['tableName'], field['name'], fieldType))
        conn.commit()
createPgTables(parsedXSD, conn, cursor)
conn.close()
