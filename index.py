from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, \
        DB_SCHEMA, XSD_DIRECTORY, XML_DIRECTORY, REGION_CODE
from connection import connectToDB
from parseXSD import parseXsd
from createPgTables import createPgTables
from fillPgTables import fillPgTables
from createIndexes import createIndexes
(connection, cursor) = connectToDB(
  DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)

cursor.execute("CREATE SCHEMA IF NOT EXISTS {schema};" \
    .format(schema=DB_SCHEMA))
print('--- Создана схема {schema} ---'.format(schema=DB_SCHEMA))

parsedXSD = parseXsd(XSD_DIRECTORY)

createPgTables(parsedXSD, connection, cursor, DB_SCHEMA)

fillPgTables(
  XML_DIRECTORY, XSD_DIRECTORY, cursor, connection, DB_SCHEMA, REGION_CODE)

createIndexes(parsedXSD, connection, cursor, DB_SCHEMA)

connection.close()