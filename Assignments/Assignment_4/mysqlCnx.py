import pymysql

def query(database,sql,returnType):
    print(database, sql, returnType)
    result = -1
    try:
        connection = pymysql.connect(host='localhost',
                                    user='kanrailsql',
                                    password='ZX88**zxcv',
                                    database = database,
                                    cursorclass=pymysql.cursors.DictCursor)
        with connection:
            if returnType != 'select' and returnType != 'update':
                with connection.cursor() as cursor:
                    result = cursor.execute(sql)

                    cursor.commit()
            elif returnType == 'update':
                with connection.cursor() as cursor:
                    result = cursor.execute(sql)
                    connection.commit()
            else:
                with connection.cursor() as cursor:
                    cursor.execute(sql)
                    result = cursor.fetchall()
        return result
    except:
        return {'error':'invalid query'}

def sprocQuery(database,data,proc,returnType):
    result = -1
    print(database,data,proc,returnType)
    try:
        connection = pymysql.connect(host='localhost',
                                    user='kanrailsql',
                                    password='ZX88**zxcv',
                                    database = database,
                                    cursorclass=pymysql.cursors.DictCursor)
        with connection:
            if returnType != 'select':
                with connection.cursor() as cursor:
                    result = cursor.callproc(proc,data)
                    print(result)
            else:
                with connection.cursor() as cursor:
                    cursor.callproc(proc,data)
                    print(result)
                    result = cursor.fetchall()
        return result
    except:
        return {'error':'invalid query'}