import os
import lxml.etree as et
from progress.bar import IncrementalBar

def insertIntoDb(XMLdirectory, item, schema, cursor, conn):
    print('----- Таблица {0} заполняется... -----'.format(item[3:item.find('_20')]))
    tree = et.parse(os.path.join(XMLdirectory, item))
    root = tree.getroot()
    if root.__len__() > 0:
        dLength = root.__len__()
        bar = IncrementalBar('Progress', max=dLength)
        for child in root:
            columns = ''
            values = ''
            updateSet = ''
            for attrib in child.attrib.items():
                columns = columns + '"{0}", '.format(attrib[0].lower())
                values = values + '\'{0}\', '.format(str(attrib[1]))
                updateSet = updateSet + '"{0}" = EXCLUDED.{0}, '.format(attrib[0].lower())
            bar.next()
            tableName = 'HOUSE_TYPES' if item[3:item.find('_20')] == 'ADDHOUSE_TYPES' else item[3:item.find('_20')]
            if tableName == 'CHANGE_HISTORY':
                cursor.execute('INSERT INTO {0}.{1} ({2}) VALUES ({3}) ON CONFLICT DO NOTHING;' \
                    .format(schema, tableName, columns[:-2], values[:-2]))
            elif tableName == 'REESTR_OBJECTS':
                cursor.execute('INSERT INTO {0}.{1} ({2}) VALUES ({3}) ON CONFLICT (objectid, changeid) DO UPDATE SET {4};' \
                    .format(schema, tableName, columns[:-2], values[:-2], updateSet[32:-2]))
            elif tableName == 'OBJECT_LEVELS':
                cursor.execute('INSERT INTO {0}.{1} ({2}) VALUES ({3}) ON CONFLICT (level) DO UPDATE SET {4};' \
                    .format(schema, tableName, columns[:-2], values[:-2], updateSet[26:-2]))
            else:
                cursor.execute('INSERT INTO {0}.{1} ({2}) VALUES ({3}) ON CONFLICT (id) DO UPDATE SET {4};' \
                    .format(schema, tableName, columns[:-2], values[:-2], updateSet[20:-2]))
            
        conn.commit()

        bar.finish()
        print('----- ГОТОВО -----')
    else:
        print('----- НЕТ ДАННЫХ -----')

if __name__ == "__main__":
    insertIntoDb(
        '/media/first/GAR/XML/30', 
        'AS_ADDR_OBJ_DIVISION_20211216_ffd54515-2038-4f32-9ff1-4465194f7105.XML',
        'aar',
        'cur',
        'conn'
        )