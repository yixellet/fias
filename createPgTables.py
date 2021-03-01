def createPgTables(parsedXSD, conn, cursor, schemaName):
    """
    Создание таблиц в БД PostgreSQL

    Функция принимает массив разобранных XSD файлов, конвертированных в словари,
    объект соединения с БД и объект курсора.
    Создает из каждого XSD отдельную таблицу в БД.
    """

    for schema in parsedXSD:
        fields = ''
        for field in schema['fields']:
            if field['type'] == 'character varying':
                fields = fields + '"{0}" {1} ({2}), '.format(field['name'], field['type'], field['length'])
            else:
                fields = fields + '"{0}" {1}, '.format(field['name'], field['type'])
        fields = fields[:-2]
        c = {'name': 'id'}
        for field in schema['fields']:
            if c.items() <= field.items():
                fields = fields + ', PRIMARY KEY ("id")'
        if schema['fileName'][3:schema['fileName'].find('_2')] == 'CHANGE_HISTORY':
            fields = fields + ', PRIMARY KEY ("changeid")'
        elif schema['fileName'][3:schema['fileName'].find('_2')] == 'OBJECT_LEVELS':
            fields = fields + ', PRIMARY KEY ("level")'
        elif schema['fileName'][3:schema['fileName'].find('_2')] == 'REESTR_OBJECTS':
            fields = fields + ', PRIMARY KEY ("objectid", "changeid")'
        if schema['tableName'] == 'PARAMS':
            cursor.execute(
                'CREATE TABLE IF  NOT EXISTS {0}."addr_obj_params" ({1});'.format(schemaName, fields)
            )
            cursor.execute(
                'CREATE TABLE IF  NOT EXISTS {0}."apartments_params" ({1});'.format(schemaName, fields)
            )
            cursor.execute(
                'CREATE TABLE IF  NOT EXISTS {0}."carplaces_params" ({1});'.format(schemaName, fields)
            )
            cursor.execute(
                'CREATE TABLE IF  NOT EXISTS {0}."houses_params" ({1});'.format(schemaName, fields)
            )
            cursor.execute(
                'CREATE TABLE IF  NOT EXISTS {0}."rooms_params" ({1});'.format(schemaName, fields)
            )
            cursor.execute(
                'CREATE TABLE IF  NOT EXISTS {0}."steads_params" ({1});'.format(schemaName, fields)
            )
        else:
            cursor.execute(
                "CREATE TABLE IF  NOT EXISTS {0}.{1} ({2});".format(schemaName, schema['fileName'][3:schema['fileName'].find('_2')], fields)
            )
        print(fields)
    conn.commit()
    print('--- Созданы таблицы в БД ---')