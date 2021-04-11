
import os
from datetime import datetime

from urllib.request import urlopen

from fetchFiasApi import fetchFiasApi
from dateConverter import convertStringToDate
from config import UPDATE_SERVICE_URL

def checkUpdate(updDir, logFile):
    currentVersionDateFile = open(os.path.join(updDir, 'currentVersion.txt'))

    lastAccessibleVersion = fetchFiasApi(UPDATE_SERVICE_URL, 'update')
    lastVerrsionDate = convertStringToDate(lastAccessibleVersion['Date']) 

    currentVersionDate = convertStringToDate(currentVersionDateFile.read())
    currentVersionDateFile.close()

    if lastVerrsionDate > currentVersionDate:
        fileSize = urlopen(lastAccessibleVersion['GarXMLURL']).headers['Content-Length']
        if fileSize < 1073741824:
            return lastAccessibleVersion
        else:
            logFile.write(str(datetime.now()) + ' --- ВНИМАНИЕ!!! \
            Размер файла версии {0} превышает 1ГБ. Проверьте файл на сайте \
            ФНС ---\n'.format(lastAccessibleVersion['VersionId']))
            logFile.close()
            return 'No Updates'
    else:
        logFile.write(str(datetime.now()) + ' --- Обновлений не обнаружено. \
        Текущая версия {0} ---\n'.format(lastAccessibleVersion['VersionId']))
        logFile.close()
        return 'No Updates'