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
                'CREATE INDEX {0}_id_idx ON {1}."{0}" USING btree ("id")' \
                .format((schema['fileName'][3:schema['fileName'].find('_2')]).lower(), schemaName)
            )
    cursor.execute('CREATE INDEX {1}_{2}_idx ON {0}."{1}" USING btree ("{2}")' \
        .format(schemaName, 'change_history', 'changeid')
    )

    for table in tablesArray:
        cursor.execute(
            'CREATE INDEX {1}_{2}_idx ON {0}."{1}" USING btree ("{2}")' \
            .format(schemaName, table, 'objectid')
        )
        cursor.execute(
            'CREATE INDEX {1}_{2}_idx ON {0}."{1}" USING btree ("{2}")' \
            .format(schemaName, table, 'previd')
        )
        cursor.execute(
            'CREATE INDEX {1}_{2}_idx ON {0}."{1}" USING btree ("{2}")' \
            .format(schemaName, table, 'nextid')
        )
    hierarchyTables = ['adm_hierarchy', 'mun_hierarchy']
    for table in hierarchyTables:
        cursor.execute(
            'CREATE INDEX IF NOT EXISTS {1}_objectid_idx \
                ON {0}.{1} USING btree \
                (objectid ASC NULLS LAST) \
                TABLESPACE pg_default; \
            CREATE INDEX IF NOT EXISTS {1}_parentobjid_idx \
                ON {0}.{1} USING btree \
                (parentobjid ASC NULLS LAST) \
                TABLESPACE pg_default;' \
            .format(schemaName, table)
        )
    conn.commit()
    print('--- Индексы созданы ---')
