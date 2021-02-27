import urllib.request
import json

def fetchFiasApi(url: str, regime: str):
    """
    Функция принимает URL службы обновлений ФИАС и режим работы.
    Возвращает VersionId последней доступной версии справочника
    и её URL.
    @url {string} -- адрес службы обновлений
    @regime {string} -- 'full' или 'update'
    """
    if regime == 'full':
        fileType =  'GarXMLFullURL'
    elif regime == 'update':
        fileType = 'GarXMLDeltaURL'

    with urllib.request.urlopen(url) as response:
        versions = json.loads(response.read())

    if (versions[0][fileType] != ''):
        VersionId = versions[0]["VersionId"]
        GarXMLURL = versions[0][fileType]
        date = versions[0]['Date']
    else:
        VersionId = versions[1]['VersionId']
        GarXMLURL = versions[1][fileType]
        date = versions[1]['Date']

    return {
        'VersionId': VersionId,
        'GarXMLURL': GarXMLURL,
        'Date': date
    }