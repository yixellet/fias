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

#schema = open(r'D:\\fias_gar_15092020\\Schemas\\AS_ADDR_OBJ_2_251_01_04_01_01.XSD', 'r', encoding='utf_8_sig')
schema = open('/mnt/bad63750-d3a5-46f9-9477-a5075147cae2/fias/gar_delta/Schemas/AS_ADDR_OBJ_2_251_01_04_01_01.XSD','r',encoding='utf_8_sig')
schemadict = {}
schemastr = schema.read()

def extractContent(xsd):
    string = xsd.replace('\n','').replace('\t','')
    return string[string.find('<xs:', 0):]

"""
def parser(string, dictionary=0):
    
    # Функция записывает индекс открывающего и закрывающего тегов, вызывает себя и передает себе текст между тегами
    
    if string.find('<xs:') == -1:
        pass
    else:
        openTagStartIndex = string.find('<xs:')
        openTagNameWithAttributes = string[openTagStartIndex:string.find('>')+1]
        openTagNameClear = openTagNameWithAttributes[4:re.search(r'\ |>', openTagNameWithAttributes).start()]
        closeTagName = '</xs:' + openTagNameClear
        closeTagStartIndex = string.find(closeTagName)
        tagContent = string[openTagStartIndex+len(openTagNameWithAttributes):closeTagStartIndex]
        dictionary['tag'] = openTagNameClear
        dictionary[openTagNameClear] = {}
        parser(tagContent,dictionary[openTagNameClear],closeTagStartIndex + len(closeTagName)+1)
"""
openTags = []
def diver(string, ellist, openTags=openTags):

    if len(string) < 2:
        return 'Search complete'

    if string.find('<xs:') != -1 and string.find('</xs') != -1 and string.find('<xs:') < string.find('</xs'):
        openTagStartIndex = string.find('<xs:')
        openTagNameWithAttributes = string[openTagStartIndex:string.find('>')+1]
        openTagNameClear = openTagNameWithAttributes[4:re.search(r'\ |>', openTagNameWithAttributes).start()]
        openTags.append(openTagNameClear)
        if openTagNameWithAttributes.find(' name=') != -1:
            ellist.append(openTagNameWithAttributes[openTagNameWithAttributes.find(' name=')+7:openTagNameWithAttributes.find('"',openTagNameWithAttributes.find(' name=')+8)])
        if openTagNameWithAttributes[-2] == '/':
            openTags.pop()
        diver(string[openTagStartIndex+len(openTagNameWithAttributes):],ellist)
    else:
        openTags.pop()
        closeTagStartIndex = string.find('</xs:')
        closeTagName = string[closeTagStartIndex:string.find('>')+1]
        diver(string[closeTagStartIndex+len(closeTagName):],ellist)


elements = []

string = extractContent(schemastr)
diver(string, elements)
print(elements)

schema.close()