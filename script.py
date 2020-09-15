import urllib.request
import json
import zipfile

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