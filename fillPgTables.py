import os
import xmlschema

def fillPgTables(XMLdirectory, XSDdirectory, cursor, conn, schema):
    for item in os.listdir(XMLdirectory):
        if item.find('.XML') != -1:
            if item.find('PARAMS') == -1:
                for file in os.listdir(XSDdirectory):
                    if file.find(item[:item.index('_2')]) != -1:
                        xs = xmlschema.XMLSchema('{0}/{1}'.format(XSDdirectory, file))
                        data = xs.to_dict('{0}/{1}'.format(XMLdirectory, item))
            else:
                for file in os.listdir(XSDdirectory):
                    if file.find('AS_PARAM_2') != -1:
                        xs = xmlschema.XMLSchema('{0}/{1}'.format(XSDdirectory, file))
        
        if item == '30':
            fillPgTables(XMLdirectory + '/' + item, XSDdirectory, cursor, conn, schema)


"""
        if item.find('.XML') != -1:
            if item[3:item.find('_2')] in list(parsedXSD.keys()):
                data = parsedXSD[item[3:item.find('_2')]]['object'].to_dict(directory + '/' + item)
                
                if data != None:
                    for line in data[list(data.keys())[0]]:
                        columns = ''
                        values = ''
                        for key in line:
                            columns = columns + '"' + str(key[1:]).lower() + '", '
                            values = values + '\'' + str(line[key]) + '\', '
                        print("INSERT INTO {3}.{0} ({1}) VALUES ({2});".format(item[3:item.find('_2')].lower(), columns[:-2], values[:-2], schema))
                        cursor.execute("INSERT INTO {3}.{0} ({1}) VALUES ({2});".format(item[3:item.find('_2')].lower(), columns[:-2], values[:-2], schema))
                    conn.commit()
                
            if item.find('PARAMS_2') != -1:
                data = parsedXSD['PARAM']['object'].to_dict(directory + '/' + item)
                if data != None:
                    for line in data[list(data.keys())[0]]:
                        columns = ''
                        values = ''
                        for key in line:
                            columns = columns + '"' + str(key[1:]).lower() + '", '
                            values = values + '\'' + str(line[key]) + '\', '
                        print("INSERT INTO {3}.{0} ({1}) VALUES ({2});".format(item[3:item.find('_2')].lower(), columns[:-2], values[:-2], schema))
                        cursor.execute("INSERT INTO {3}.{0} ({1}) VALUES ({2});".format(item[3:item.find('_2')].lower(), columns[:-2], values[:-2], schema))
                    conn.commit()
"""