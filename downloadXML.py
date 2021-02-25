import urllib.request
import json
import zipfile
import os

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