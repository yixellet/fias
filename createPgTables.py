import os

def createPgTables(directory, parsedXSD, conn, cursor, schema):
    """
    Создание таблиц в БД PostgreSQL

    Функция принимает директорию с XML, массив разобранных XSD файлов, конвертированных в словари,
    объект соединения с БД и объект курсора.
    Создает из каждого XSD отдельную таблицу в БД.
    """
    for item in os.listdir(directory):
        if item.find('.XML') != -1:
            if item[3:item.find('_2')] in list(parsedXSD.keys()):
                cursor.execute("CREATE TABLE IF NOT EXISTS {2}.{0} ({1} bigint CONSTRAINT {0}_{1}_pk PRIMARY KEY);".format(item[3:item.find('_2')], parsedXSD[item[3:item.find('_2')]]['fields'][0]['name'].lower(), schema))
                
                conn.commit()
                for field in parsedXSD[item[3:item.find('_2')]]['fields'][1:]:
                    if field['type'] == 'character varying':
                        cursor.execute("ALTER TABLE {4}.{0} ADD COLUMN \"{1}\" {2}({3});".format(item[3:item.find('_2')], field['name'].lower(), field['type'], field['length'], schema))
                    if field['type'] == 'date' or field['type'] == 'boolean' or field['type'] == 'bigint':
                        cursor.execute("ALTER TABLE {3}.{0} ADD COLUMN \"{1}\" {2};".format(item[3:item.find('_2')], field['name'].lower(), field['type'], schema))
                
            if item.find('PARAMS_2') != -1:
                cursor.execute("CREATE TABLE IF NOT EXISTS {2}.{0} ({1} bigint CONSTRAINT {0}_{1}_pk PRIMARY KEY);".format(item[3:item.find('_2')], parsedXSD['PARAM']['fields'][0]['name'].lower(), schema))
                conn.commit()
                for field in parsedXSD['PARAM']['fields'][1:]:
                    if field['type'] == 'character varying':
                        cursor.execute("ALTER TABLE {4}.{0} ADD COLUMN \"{1}\" {2}({3});".format(item[3:item.find('_2')], field['name'].lower(), field['type'], field['length'], schema))
                    if field['type'] == 'date' or field['type'] == 'boolean' or field['type'] == 'bigint':
                        cursor.execute("ALTER TABLE {3}.{0} ADD COLUMN \"{1}\" {2};".format(item[3:item.find('_2')], field['name'].lower(), field['type'], schema))
        if item == '30':
            createPgTables(directory + '/' + item, parsedXSD, conn, cursor)
            
        conn.commit()
