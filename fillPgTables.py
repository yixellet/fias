import os
import xmlschema
from progress.bar import IncrementalBar
from time import sleep

def insertIntoDb(XSDdirectory, XMLdirectory, file, item, schema, cursor, conn, mode):
    print('----- Таблица {0} заполняется... -----'.format(item[3:item.find('_20')]))
    xs = xmlschema.XMLSchema(os.path.join(XSDdirectory, file))
    data = xs.to_dict(source=os.path.join(XMLdirectory, item), validation='skip')
    if data != None:
        bar = IncrementalBar('Progress', max=len(data[list(data.keys())[0]]))
        for line in data[list(data.keys())[0]]:
            columns = ''
            values = ''
            for pair in line.items():
                columns = columns + '"{0}", '.format(pair[0][1:].lower())
                values = values + '\'{0}\', '.format(str(pair[1]))
            if mode == 'prod':
                bar.next()
                cursor.execute('INSERT INTO {0}.{1} ({2}) VALUES ({3}) ON CONFLICT DO NOTHING;' \
                    .format(schema, item[3:item.find('_20')], columns[:-2], values[:-2]))
                
                if data[list(data.keys())[0]].index(line) % 1000 == 0:
                    conn.commit()
            elif mode == 'test':
                print('INSERT' + str(data[list(data.keys())[0]].index(line)))
                if data[list(data.keys())[0]].index(line) % 5000 == 0 or data[list(data.keys())[0]].index(line) == len(data[list(data.keys())[0]]) - 1:
                    print('COMMIT!!')

        bar.finish()
        print('----- ГОТОВО -----')
    else:
        print('----- НЕТ ДАННЫХ -----')

def fillPgTables(XMLdirectory, XSDdirectory, cursor, conn, schema, regionCode, mode='prod'):
    print(os.listdir(XMLdirectory))
    for item in os.listdir(XMLdirectory):
        if item.find('.XML') != -1:
            if item.find('PARAMS') == -1:
                for file in os.listdir(XSDdirectory):
                    if file[:file.index('_2')] == item[:item.index('_2')]:
                        insertIntoDb(XSDdirectory, XMLdirectory, file, item, schema, cursor, conn, mode)
            else:
                for file in os.listdir(XSDdirectory):
                    if file.find('AS_PARAM_2') != -1:
                        insertIntoDb(XSDdirectory, XMLdirectory, file, item, schema, cursor, conn, mode)
        elif item == regionCode:
            fillPgTables(os.path.join(XMLdirectory, item), XSDdirectory, cursor, conn, schema, regionCode, mode)
    print('--- Все таблицы заполнены ---')

if __name__ == "__main__":
    from connection import connectToDB
    from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, \
        DB_SCHEMA, XSD_DIRECTORY, REGION_CODE
    XML_DIRECTORY = 'D:\\dev\\GAR\\XML-2'
    (connection, cursor) = connectToDB(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)
    fillPgTables(XML_DIRECTORY, XSD_DIRECTORY, cursor, connection, DB_SCHEMA, REGION_CODE, 'test')