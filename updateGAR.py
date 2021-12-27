import os
import shutil
from datetime import datetime

from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, \
        DB_SCHEMA, XSD_DIRECTORY, REGION_CODE, UPDATE_DIRECTORY, \
        UPDATE_SERVICE_URL
from fetchFiasApi import fetchFiasApi
from dateConverter import convertStringToDate
from downloadAndUnzip import downloadAndUnzip
from validateXML import batchValidation
from connection import connectToDB
from fillPgTables import fillPgTables
from updateIndexes import updateIndexes

log = open(os.path.join(UPDATE_DIRECTORY, 'log.txt'), 'a')
currentVersionDateFile = open(os.path.join(UPDATE_DIRECTORY, 'currentVersion.txt'))
currentVersionDate = convertStringToDate(currentVersionDateFile.read())
currentVersionDateFile.close()

availableVersions = fetchFiasApi(UPDATE_SERVICE_URL, 'update', currentVersionDate)

if len(availableVersions) != 0:
    print(str(datetime.now()) + '\nДоступно обновлений: ' + str(len(availableVersions)))
    log.write(str(datetime.now()) + '\nДоступно обновлений: ' + str(len(availableVersions)) + '\n')
    for version in availableVersions:
        print('\tДата: ' + version['Date'] + ', размер файла: ' + str(round(version['Size']/1024/1024)) + ' МБ')
        log.write('\tДата: ' + version['Date'] + ', размер файла: ' + str(round(version['Size']/1024/1024)) + ' МБ' + '\n')
    
    print('Необходимо выполнить ' + str(len(availableVersions)) + ' процедур обновления справочника')
    input('Enter')
    for version in availableVersions[::-1]:
        print('Обновление от ' + version['Date'])
        log.write('Обновление от ' + version['Date'] + '\n')
        if version['Size'] > 1073741824:
            print('\tВНИМАНИЕ!!! \
            Размер файла версии {0} превышает 1ГБ. Проверьте файл на сайте \
            ФНС ---\n'.format(version['VersionId']))
            log.write('\tВНИМАНИЕ!!! \
            Размер файла версии {0} превышает 1ГБ. Проверьте файл на сайте \
            ФНС ---\n'.format(version['VersionId']))
            log.close()
        else:
            print('\tЗагрузка...')
            downloadAndUnzip(
                version['GarXMLURL'], 
                version['VersionId'], 
                UPDATE_DIRECTORY,
                REGION_CODE)
            print('\tЗагружено.')
            log.write('\tЗагружено.\n')
            validation = batchValidation(UPDATE_DIRECTORY, XSD_DIRECTORY, REGION_CODE)
            for file in validation:
                if file['IsValid'] is False:
                    print('\t' + file['File'] + '\t' + str(file['IsValid']))
                    log.write('\t' + file['File'] + '\t' + str(file['IsValid']) + '\n')
            
            (connection, cursor) = connectToDB(
                DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)
            fillPgTables(UPDATE_DIRECTORY, cursor, connection, DB_SCHEMA, REGION_CODE)
            updateIndexes(cursor, connection, DB_SCHEMA)
            connection.close()
            log.write(' --- Обновленo. Текущая версия {0} ---\n'.format(version['VersionId']))
            currentVersionDateFile = open(os.path.join(UPDATE_DIRECTORY, 'currentVersion.txt'), 'w')
            currentVersionDateFile.write(version['Date'])
            currentVersionDateFile.close()
            for file in os.listdir(UPDATE_DIRECTORY):
                if file.find('.txt') == -1:
                    if file == '30':
                        shutil.rmtree(os.path.join(UPDATE_DIRECTORY, file))
                    else:
                        os.remove(os.path.join(UPDATE_DIRECTORY, file))
    
    log.close()
