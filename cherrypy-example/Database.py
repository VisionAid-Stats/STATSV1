import mysql.connector


class Database:
    def __init__(self):
        self.host = 'visionaid-db1.cwpyfpvknmbu.us-east-1.rds.amazonaws.com'
        self.user = 'VisionAidAdmin'
        self.password = 'Vi$i0n-AidPW#'
        self.database = 'visionaiddb1'

    def connect(self):
        db = mysql.connector.connect(host=self.host, user=self.user, password=self.password)
        db.database = self.database
        return db

    def execute_select(self, statement='SELECT 1', params=()):
        ret = []
        db = self.connect()
        cursor = db.cursor(buffered=True)
        cursor.execute(statement, params)
        for row in cursor.fetchall():
            d = {}
            for i in range(len(cursor.column_names)):
                d[cursor.column_names[i]] = row[i]
            ret.append(d)
        cursor.close()
        db.close()
        return ret

    def execute_insert(self, table, columns=(), values=()):
        statement = 'INSERT INTO %s (%s) VALUES (%s)' % (table, ','.join(columns), ','.join(['%s'] * len(values)))
        db = self.connect()
        cursor = db.cursor(buffered=True)
        cursor.execute(statement, values)
        db.commit()
        cursor.close()
        db.close()
