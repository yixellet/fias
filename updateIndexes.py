def updateIndexes(cursor, connection, schema):
    cursor.execute('SELECT * FROM pg_tables WHERE schemaname=\'{0}\';'.format(schema))
    tables = []
    for record in cursor:
        tables.append(record[1])
    for table in tables:
        cursor.execute('REINDEX TABLE {0}.{1};'.format(schema, table))
    connection.commit()
    print('--- Индексы обновлены ---')

if __name__ == "__main__":
    from connection import connectToDB
    from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DB_SCHEMA
    (connection, cursor) = connectToDB(
        DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)
    updateIndexes(cursor, connection, DB_SCHEMA)
