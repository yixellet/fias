
import os
from datetime import datetime

from urllib.request import urlopen

from fetchFiasApi import fetchFiasApi
from dateConverter import convertStringToDate

def checkUpdate(updDir: str, logFile: object, updServiceUrl: str):
    """
    Проверяет наличие обновлений ГАР на сайте ФНС.
    @updDir {string} - директория, связанная с обновлениями. В ней содержатся:
                       log.txt - файл для записи логов обновлений
                       currentVersion.txt - файл, в котором записана текущая
                       версия ГАР в формате "дд.мм.гггг"
    @logfile {object}  файл log.txt, открытый функцией open()
    @updateServiceUrl {string} - адрес службы получения обновлений ГАР

    Модуль обращается к службе обнорвлений ГАР, получает оттуда дату последней
    доступной версии, сравнивает с датой из файла currentVersion.txt.
    Возвращаемые значения:
    1) при наличии новой версии
    """
    currentVersionDateFile = open(os.path.join(updDir, 'currentVersion.txt'))
    currentVersionDate = convertStringToDate(currentVersionDateFile.read())
    currentVersionDateFile.close()

    lastAccessibleVersion = fetchFiasApi(updServiceUrl, 'update', currentVersionDate)
    lastVerrsionDate = convertStringToDate(lastAccessibleVersion['Date']) 


    if lastVerrsionDate > currentVersionDate:
        fileSize = urlopen(lastAccessibleVersion['GarXMLURL']).headers['Content-Length']
        if int(fileSize) < 1073741824:
            print('Доступна новая версия! ' + lastVerrsionDate.strftime("%d.%m.%Y"))
            return lastAccessibleVersion
        else:
            logFile.write(str(datetime.now()) + ' --- ВНИМАНИЕ!!! \
            Размер файла версии {0} превышает 1ГБ. Проверьте файл на сайте \
            ФНС ---\n'.format(lastAccessibleVersion['VersionId']))
            logFile.close()
            return 'WARNING !!!'
    else:
        logFile.write(str(datetime.now()) + ' --- Обновлений не обнаружено. \
        Текущая версия {0} ---\n'.format(lastAccessibleVersion['VersionId']))
        logFile.close()
        return 'No Updates'


if __name__ == "__main__":

    UPDATE_SERVICE_URL='http://fias.nalog.ru/WebServices/Public/GetAllDownloadFileInfo'
    updDir = '/media/first/GAR/update'
    log = open(os.path.join(updDir, 'log.txt'), 'a')
    checkUpdate(updDir, log, UPDATE_SERVICE_URL)