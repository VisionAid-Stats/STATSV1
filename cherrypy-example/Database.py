import mysql.connector


class Database:
    _connection = None

    def __init__(self):
        if not Database._connection:
            Database._connection = mysql.connector.connect(host='visionaid-db1.cwpyfpvknmbu.us-east-1.rds.amazonaws.com',
                                                  user='VisionAidAdmin',
                                                  password='Vi$i0n-AidPW#')
            Database._connection.database = 'visionaiddb1'
        self.db = Database._connection

    def get_cursor(self):
        return self.db.cursor(buffered=True)

    def close(self):
        self.db.close()

    def execute_select(self, statement='SELECT 1', params=()):
        ret = []
        cursor = self.get_cursor()
        cursor.execute(statement, params)
        for row in cursor.fetchall():
            d = {}
            for i in range(len(cursor.column_names)):
                d[cursor.column_names[i]] = row[i]
            ret.append(d)
        cursor.close()
        return ret

    def execute_insert(self, table, columns=(), values=()):
        statement = 'INSERT INTO %s (%s) VALUES (%s)' % (table, ','.join(columns), ','.join(['%s'] * len(values)))
        cursor = self.get_cursor()
        cursor.execute(statement, values)
        self.db.commit()
        cursor.close()
