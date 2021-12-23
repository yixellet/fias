import os

import xmlschema

def insertIntoDb(XSDdirectory, XMLdirectory, file, item, schema, cursor, conn):
    print('----- Таблица {0} заполняется... -----'.format(item[3:item.find('_20')]))
    xs = xmlschema.XMLSchema(os.path.join(XSDdirectory, file))
    data = xs.to_dict(source=os.path.join(XMLdirectory, item), validation='skip')
    if data != None:
        for line in data[list(data.keys())[0]]:
            columns = ''
            values = ''
            for pair in line.items():
                columns = columns + '"{0}", '.format(pair[0][1:].lower())
                values = values + '\'{0}\', '.format(str(pair[1]))
            cursor.execute('INSERT INTO {0}.{1} ({2}) VALUES ({3}) ON CONFLICT DO NOTHING;' \
                .format(schema, item[3:item.find('_20')], columns[:-2], values[:-2]))
        conn.commit()
        print('----- ГОТОВО -----')
    else:
        print('----- НЕТ ДАННЫХ -----')

def fillPgTables(XMLdirectory, XSDdirectory, cursor, conn, schema, regionCode):
    for item in os.listdir(XMLdirectory):
        if item.find('.XML') != -1:
            if item.find('PARAMS') == -1:
                for file in os.listdir(XSDdirectory):
                    if file[:file.index('_2')] == item[:item.index('_2')]:
                        insertIntoDb(XSDdirectory, XMLdirectory, file, item, schema, cursor, conn)
            else:
                for file in os.listdir(XSDdirectory):
                    if file.find('AS_PARAM_2') != -1:
                        insertIntoDb(XSDdirectory, XMLdirectory, file, item, schema, cursor, conn)
        elif item == regionCode:
            fillPgTables(os.path.join(XMLdirectory, item), XSDdirectory, cursor, conn, schema, regionCode)
    print('--- Все таблицы заполнены ---')
