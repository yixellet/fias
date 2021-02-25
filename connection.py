import psycopg2

def connectToDB(dbhost, dbport, dbuser, dbpassword, dbname, dbschema):
    try:
        connection = psycopg2.connect(
            'dbname={dbname} user={dbuser} password={dbpassword} host={dbhost}' \
            .format(dbname=dbname, dbuser=dbuser, dbpassword=dbpassword, dbhost=dbhost)
        )
        print('--- Соединение с БД установлено ---')
    except psycopg2.Error as e:
        print(e)
    cursor = connection.cursor()

    cursor.execute("CREATE SCHEMA IF NOT EXISTS {schema};" \
        .format(schema=dbschema))
    print('--- Создана схема {schema} ---'.format(schema=dbschema))
    connection.commit()
    return connection, cursor