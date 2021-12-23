from datetime import datetime, date
from urllib.request import urlopen
import json
from dateConverter import convertStringToDate


def fetchFiasApi(url: str, regime: str, curDate: datetime = None):
    """
    Функция принимает URL службы обновлений ФИАС и режим работы.
    Возвращает VersionId последней доступной версии справочника
    и её URL.
    @url {string} - адрес службы обновлений
    @regime {string} - 'full' или 'update'
    @curDate {datetime} - дата установленной версии ГАР (обязательна только в
                          режиме 'update')

    Возвращает список словарей:
    1) в режиме 'full' - в списке один словарь
        {
            VersionId: ID последней доступной версии справочника,
            GarXMLURL: ссылка для скачивания этой версии,
            Date: дата этой версии
        };
    2) в режиме 'update' - количество словарей соответствует количеству
        версий ГАР, которые необходимо загрузить для полного обновления
    """

    with urlopen(url) as response:
        versions = json.loads(response.read())
    
    result = []
    if regime == 'full':
        for version in versions:
            if version['GarXMLFullURL'] != '':
                result.append({
                    'VersionId': version['VersionId'],
                    'GarXMLURL': version['GarXMLFullURL'],
                    'Date': version['Date'],
                    'Size': int(urlopen(version['GarXMLFullURL']).headers['Content-Length'])
                })
                break

    elif regime == 'update':
        for version in versions:
            if version['GarXMLDeltaURL'] != '' and convertStringToDate(version['Date']) > curDate:
                result.append({
                    'VersionId': version['VersionId'],
                    'GarXMLURL': version['GarXMLDeltaURL'],
                    'Date': version['Date'],
                    'Size': int(urlopen(version['GarXMLDeltaURL']).headers['Content-Length'])
                })

    return result

if __name__ == "__main__":
    UPDATE_SERVICE_URL='http://fias.nalog.ru/WebServices/Public/GetAllDownloadFileInfo'
    print(fetchFiasApi(UPDATE_SERVICE_URL, 'full'))
    print(fetchFiasApi(UPDATE_SERVICE_URL, 'update', date(2021, 12, 14)))