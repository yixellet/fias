import urllib.request
import json
import zipfile
import psycopg2
import xmlschema
from pprint import pprint
import re
"""
with urllib.request.urlopen('http://fias.nalog.ru/WebServices/Public/GetLastDownloadFileInfo') as response:
    versions = json.loads(response.read())

GarXMLFullURL = versions["GarXMLFullURL"]

url = urllib.request.urlretrieve(versions["GarXMLDeltaURL"], '/media/owgrant/second/fias/gar_delta.zip')

gar_zip = zipfile.ZipFile('/media/owgrant/second/fias/gar_delta.zip')

for file in gar_zip.namelist():
    if file.find('/') != -1:
        if file.split('/')[0] == '30' or file.split('/')[0] == 'Schemas':
            gar_zip.extract(file, '/media/owgrant/second/fias/gar_delta/')
    else:
        gar_zip.extract(file, '/media/owgrant/second/fias/gar_delta/')

try:
    conn = psycopg2.connect("dbname=geodata user=postgres password=07071907 host=localhost")
except psycopg2.Error as e:
    print(e)
cursor = conn.cursor()
cursor.execute("CREATE SCHEMA fias;")

cursor.close()
conn.commit()
conn.close()
"""

schema = open(r'D:\\fias_gar_15092020\\Schemas\\AS_ADDR_OBJ_2_251_01_04_01_01.XSD', 'r', encoding='utf_8_sig')
#schema = xmlschema.XMLSchema('/media/owgrant/second/fias/gar_delta/Schemas/AS_ADDR_OBJ_2_251_01_04_01_01.XSD')
position = 0


schemadict = []

schemastr = schema.read()

def parser(string, position=131):
    currentOpenTagIndex = string.find('<xs:', position)
    currentOpenTagWithAttributes = string[ currentOpenTagIndex:string.find('>', position)+1 ]
    print(string.find('>', position))
    currentOpenTagName = currentOpenTagWithAttributes[ currentOpenTagWithAttributes.find('xs:') : currentOpenTagWithAttributes.find(re.search(r'\ |>', currentOpenTagWithAttributes).start())]
    currentCloseTagName = '</' + currentOpenTagName
    currentCloseTagIndex = string.find('</' + currentOpenTagName, position)
    print(currentOpenTagName, ' ', currentOpenTagIndex)
    print(currentCloseTagName, ' ', currentCloseTagIndex)

parser(schemastr)

schema.close()

