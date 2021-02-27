import os
import xmlschema

def insertIntoDb(XSDdirectory, XMLdirectory, file, item, schema, cursor, conn, param):
    print('----- Таблица {0} заполняется... -----'.format(item[3:item.find('_20')]))
    xs = xmlschema.XMLSchema('{0}/{1}'.format(XSDdirectory, file))
    data = xs.to_dict('{0}/{1}'.format(XMLdirectory, item))
    if data != None:
        for line in data[list(data.keys())[0]]:
            columns = ''
            values = ''
            tableName = ''
            for pair in line.items():
                columns = columns + '"{0}", '.format(pair[0][1:])
                values = values + '\'{0}\', '.format(str(pair[1]))
            if param or (list(data.keys())[0] == 'ITEM' or list(data.keys())[0] == 'OBJECT'):
                tableName = item[3:item.find('_20')]
            elif list(data.keys())[0] == 'NDOCKIND' or list(data.keys())[0] == 'NDOCTYPE' or list(data.keys())[0] == 'REESTR_OBJECTS':
                tableName = list(data.keys())[0]
            elif list(data.keys())[0] == 'ADDR_OBJ':
                tableName = 'ADDRESSOBJECTS'
            else:
                tableName = list(data.keys())[0]+'S'
            cursor.execute('INSERT INTO {0}.{1} ({2}) VALUES ({3});' \
                .format(schema, tableName, columns[:-2], values[:-2]))
            conn.commit()
        print('----- ГОТОВО -----')

def fillPgTables(XMLdirectory, XSDdirectory, cursor, conn, schema):
    for item in os.listdir(XMLdirectory):
        if item.find('.XML') != -1:
            if item.find('PARAMS') == -1:
                for file in os.listdir(XSDdirectory):
                    if file[:file.index('_2')] == item[:item.index('_2')]:
                        insertIntoDb(XSDdirectory, XMLdirectory, file, item, schema, cursor, conn, False)
            else:
                for file in os.listdir(XSDdirectory):
                    if file.find('AS_PARAM_2') != -1:
                        insertIntoDb(XSDdirectory, XMLdirectory, file, item, schema, cursor, conn, True)
        
        if item == '30':
            fillPgTables(XMLdirectory + '/' + item, XSDdirectory, cursor, conn, schema)
    print('--- Все таблицы заполнены ---')
