def updateIndexes(cursor, connection, schema):
    cursor.execute('REINDEX SCHEMA {0};'.format(schema))
    connection.commit()
    print('--- Индексы обновлены ---')
