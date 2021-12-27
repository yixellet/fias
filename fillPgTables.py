import os
from insertIntoDB import insertIntoDb

def fillPgTables(XMLdirectory, cursor, conn, schema, regionCode):
    for item in os.listdir(XMLdirectory):
        if item.find('.XML') != -1:
            insertIntoDb(XMLdirectory, item, schema, cursor, conn)
        elif item == regionCode:
            fillPgTables(os.path.join(XMLdirectory, item), cursor, conn, schema, regionCode)
    print('--- Все таблицы заполнены ---')

if __name__ == "__main__":
    from connection import connectToDB
    from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, \
        DB_SCHEMA, REGION_CODE, XML_DIRECTORY
    (connection, cursor) = connectToDB(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)
    fillPgTables(XML_DIRECTORY, cursor, connection, DB_SCHEMA, REGION_CODE)