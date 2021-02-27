def createIndexes(parsedXSD, conn, cursor, schemaName):
    tablesArray = [
        'addr_obj',
        'apartments',
        'carplaces',
        'houses',
        'rooms',
        'steads'
    ]
    for schema in parsedXSD:
        if (schema['fileName'].find('TYPES') != -1 
            or schema['fileName'].find('DOCS') != -1):
            cursor.execute(
                'CREATE INDEX {0}_id_idx ON {1}."{0}" USING btree ("ID")' \
                .format((schema['fileName'][3:schema['fileName'].find('_2')]).lower(), schemaName)
            )
    cursor.execute('CREATE INDEX {1}_{2}_idx ON {0}."{1}" USING btree ("{2}")' \
        .format(schemaName, 'change_history', 'CHANGEID')
    )

    for table in tablesArray:
        cursor.execute(
            'CREATE INDEX {1}_{2}_idx ON {0}."{1}" USING btree ("{2}")' \
            .format(schemaName, table, 'OBJECTID')
        )
        cursor.execute(
            'CREATE INDEX {1}_{2}_idx ON {0}."{1}" USING btree ("{2}")' \
            .format(schemaName, table, 'PREVID')
        )
        cursor.execute(
            'CREATE INDEX {1}_{2}_idx ON {0}."{1}" USING btree ("{2}")' \
            .format(schemaName, table, 'NEXTID')
        )
    conn.commit()
    print('--- Индексы созданы ---')
