from config import *
from connection import connectToDB
from parseXSD import parseXsd
from createPgTables import createPgTables
from fillPgTables import fillPgTables

(connection, cursor) = connectToDB(
  DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DB_SCHEMA)

parsedXSD = parseXsd(XSD_DIRECTORY)

createPgTables(parsedXSD, connection, cursor, DB_SCHEMA)

fillPgTables(XML_DIRECTORY, XSD_DIRECTORY, cursor, connection, DB_SCHEMA)

connection.close()