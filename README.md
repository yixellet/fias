# GAR to PostgreSQL
Скрипт для загрузки и обновления данных ФИАС в формате ГАР

* * *
### Системные требования
1. Скрипт создавался и тестировался на Ubuntu. На Windows тестов не проводилось.
2. Python 3.8
3. Pip `sudo apt install python3-pip`
4. Psycopg2 `pip3 install psycopg2`
5. XmlSchema `pip3 install xmlschema`
6. PostgreSQL ^10, в котором уже должна быть создана целевая БД
* * *

### Порядок действий при первичном импорте ГАР.

#### 1. Загрузить с [сайта ФНС](https://fias.nalog.ru/Updates):
1. архив с актуальной версией ГАР ([прямая ссылка](http://fias.nalog.ru/Public/Downloads/Actual/gar_xml.zip)).
2. XSD схемы выгрузки БД ([прямая ссылка](https://fias.nalog.ru/docs/gar_schemas.zip)).

#### 2. Разархивировать скачанные архивы
XSD схемы и XML файлы должны быть распакованы в разные директории.
Для удобства таблицы в архиве разбиты на директории по субъектам РФ.
Скрипт импортирует в БД таблицы, относящиеся **только к одному** субъекту,
поэтому в директорию для XML файлов должны быть извлечены:
1. папка, соответствующая номеру импортируемого субъекта РФ
2. все файлы, находящиеся в архиве без директорий, "сверху"

#### 3. Присвоить переменным в файле config.py необходимые значения (все значения - строки)
* DB_HOST - адрес БД
* DB_PORT - порт
* DB_USER - имя пользователя БД
* DB_PASSWORD - пароль
* DB_NAME - название БД
* DB_SCHEMA - название схемы БД
* XSD_DIRECTORY - папка с XSD схемами
* XML_DIRECTORY - папка с XML таблицами
* UPDATE_DIRECTORY - папка, куда скрипт будет скачивать обновления
* REGION_CODE - код региона

#### 4. Запустить index.py и ждать

* * *

### Для автоматического обновления БД:

#### 1. Клонировать данный репозиторий на сервер с БД (или иной)
#### 2. Установить необходимые зависимости
#### 3. Присвоить переменным в файле config.py необходимые значения
#### 4. В папке `UPDATE_DIRECTORY` предварительно создать файл `currentVersion.txt`,
в котором прописать дату скачанного архива в формате dd.mm.yyyy
#### 5. Прописать в cron ежедневное выполнение скрипта `updateGAR.py`
```crontab -e```

```mm hh * * * /path/to/python/interpreter /path/to/updateGAR.py```

Скрипт сравнивает дату в файле `currentVersion.txt` с датой новейшего доступного 
обновления на сайте ФНС и, если появилось обновление, скачивает и импортирует его.