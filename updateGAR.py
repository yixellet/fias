import os
import shutil
from datetime import datetime

from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, \
        DB_SCHEMA, XSD_DIRECTORY, REGION_CODE, UPDATE_DIRECTORY, \
        UPDATE_SERVICE_URL
from fetchFiasApi import fetchFiasApi
from dateConverter import convertStringToDate
from checkUpdate import checkUpdate
from downloadAndUnzip import downloadAndUnzip
from connection import connectToDB
from fillPgTables import fillPgTables
from updateIndexes import updateIndexes

log = open(os.path.join(UPDATE_DIRECTORY, 'log.txt'), 'a')

checkUpd = checkUpdate(UPDATE_DIRECTORY, log)

if checkUpd != 'No Updates':
    """
    downloadAndUnzip(
        checkUpd['GarXMLURL'], 
        checkUpd['VersionId'], 
        UPDATE_DIRECTORY,
        REGION_CODE)"""
    (connection, cursor) = connectToDB(
        DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)
    fillPgTables(UPDATE_DIRECTORY, XSD_DIRECTORY, cursor, connection, DB_SCHEMA, REGION_CODE)
    #updateIndexes(cursor, connection, DB_SCHEMA)
    log.write(str(datetime.now()) + ' --- Обновленo. Текущая версия {0} ---\n'.format(checkUpd['VersionId']))
    log.close()
    currentVersionDateFile = open(os.path.join(UPDATE_DIRECTORY, 'currentVersion.txt'), 'w')
    currentVersionDateFile.write(checkUpd['Date'])
    currentVersionDateFile.close()
    for file in os.listdir(UPDATE_DIRECTORY):
        if file.find('.txt') == -1:
            if file == '30':
                shutil.rmtree(os.path.join(UPDATE_DIRECTORY, file))
            else:
                os.remove(os.path.join(UPDATE_DIRECTORY, file))
