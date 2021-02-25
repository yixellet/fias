import os

def fillPgTables(directory, parsedXSD, cursor, conn):
    
    for item in os.listdir(directory):
        
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
                        print("INSERT INTO fiastest.{0} ({1}) VALUES ({2});".format(item[3:item.find('_2')].lower(), columns[:-2], values[:-2]))
                        cursor.execute("INSERT INTO fiastest.{0} ({1}) VALUES ({2});".format(item[3:item.find('_2')].lower(), columns[:-2], values[:-2]))
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
                        print("INSERT INTO fiastest.{0} ({1}) VALUES ({2});".format(item[3:item.find('_2')].lower(), columns[:-2], values[:-2]))
                        cursor.execute("INSERT INTO fiastest.{0} ({1}) VALUES ({2});".format(item[3:item.find('_2')].lower(), columns[:-2], values[:-2]))
                    conn.commit()
        
        if item == '30':
            fillPgTables(directory + '/' + item, parsedXSD, cursor, conn)
