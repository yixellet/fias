import urllib.request
import zipfile
import os

def downloadAndUnzip(url, versionId, directory, region):

    fileName = urllib.request.urlretrieve(
        url, os.path.join(directory, str(versionId) + '.zip'))[0]
    gar_zip = zipfile.ZipFile(fileName)
    for file in gar_zip.namelist():
        if file.find('/') != -1:
            if file.split('/')[0] == region or file.split('/')[0] == 'Schemas':
                gar_zip.extract(file, directory)
        else:
            gar_zip.extract(file, directory)
    os.remove(os.path.join(directory, str(versionId) + '.zip'))
    print('--- Обновление загружено в директорию {0}. \
        Текущая версия справочника {1}. ---'.format(directory, str(versionId)))