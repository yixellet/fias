import urllib.request
import zipfile
import os

def downloadAndUnzip(url, versionId, directory, region):

    fileName, headers = urllib.request.urlretrieve(
        url, directory + '/' + str(versionId) + '.zip'
    )
    gar_zip = zipfile.ZipFile(fileName)
    for file in gar_zip.namelist():
        if file.find('/') != -1:
            if file.split('/')[0] == region or file.split('/')[0] == 'Schemas':
                gar_zip.extract(file, directory)
        else:
            gar_zip.extract(file, directory)
    os.remove(directory + '/' + str(versionId) + '.zip')
    print('--- Обновление загружено в директорию {0}. \
        Текущая версия справочника {1}. ---'.format(directory, str(versionId)))