import os
from datetime import datetime
from config import *
from fetchFiasApi import fetchFiasApi
from dateConverter import convertStringToDate
from downloadAndUnzip import downloadAndUnzip
from connection import connectToDB
from fillPgTables import fillPgTables

log = open(UPDATE_DIRECTORY + '/log.txt', 'a')
currentVersionDateFile = open(UPDATE_DIRECTORY + '/currentVersion.txt')

lastAccessibleVersion = fetchFiasApi(UPDATE_SERVICE_URL, 'update')
lastVerrsionDate = convertStringToDate(lastAccessibleVersion['Date']) 

currentVersionDate = convertStringToDate(currentVersionDateFile.read())
currentVersionDateFile.close()
if lastVerrsionDate > currentVersionDate:
    downloadAndUnzip(
        lastAccessibleVersion['GarXMLURL'], 
        lastAccessibleVersion['VersionId'], 
        UPDATE_DIRECTORY,
        REGION_CODE)
    (connection, cursor) = connectToDB(
        DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DB_SCHEMA)
    fillPgTables(UPDATE_DIRECTORY, XSD_DIRECTORY, cursor, connection, DB_SCHEMA, REGION_CODE)
    log.write(str(datetime.now()) + ' --- Обновленo. Текущая версия {0} ---\n'.format(lastAccessibleVersion['VersionId']))
    currentVersionDateFile = open(UPDATE_DIRECTORY + '/currentVersion.txt', 'w')
    currentVersionDateFile.write(lastAccessibleVersion['Date'])
    currentVersionDateFile.close()
    for file in os.listdir(UPDATE_DIRECTORY):
        if file.find('.txt') != -1:
            os.remove(UPDATE_DIRECTORY + '/' + file)
else:
    log.write(str(datetime.now()) + ' --- Обновлений не обнаружено. Текущая версия {0} ---\n'.format(lastAccessibleVersion['VersionId']))

log.close()
