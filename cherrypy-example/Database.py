import mysql.connector


class Database:
    def __init__(self, cert=None, key=None):
        self.host = 'visionaid-db1.cwpyfpvknmbu.us-east-1.rds.amazonaws.com'
        self.user = 'VisionAidAdmin'
        self.password = 'Vi$i0n-AidPW#'
        self.database = 'visionaiddb1'
        self.cert = cert
        self.key = key

    def connect(self):
        if self.cert is None or self.key is None:
            db = mysql.connector.connect(host=self.host, user=self.user, password=self.password)
        else:
            db = mysql.connector.connect(host=self.host, user=self.user, password=self.password,
                                         ssl_cert=self.cert, ssl_key=self.key)
        db.database = self.database
        return db, db.cursor(buffered=True)

    def execute_select(self, statement='SELECT 1', params=()):
        ret = []
        db, cursor = self.connect()
        try:
            cursor.execute(statement, params)
            for row in cursor.fetchall():
                d = {}
                for i in range(len(cursor.column_names)):
                    d[cursor.column_names[i]] = row[i]
                ret.append(d)
        finally:
            cursor.close()
            db.close()
        return ret

    def execute_insert(self, table, columns=(), values=()):
        statement = f'INSERT INTO {table} ({",".join(columns)}) VALUES ({",".join(["%s"] * len(values))})'
        db, cursor = self.connect()
        try:
            cursor.execute(statement, values)
            db.commit()
        finally:
            cursor.close()
            db.close()

    def execute_update(self, table, columns=(), values=(), where='id = 0'):
        statement = f'UPDATE {table} SET {", ".join(map(lambda c: c + " = %s", columns))} WHERE {where}'
        db, cursor = self.connect()
        try:
            cursor.execute(statement, values)
            db.commit()
        finally:
            cursor.close()
            db.close()

    def execute_delete(self, table, primary_key, key_value):
        db, cursor = self.connect()
        try:
            if type(primary_key) in (list, tuple):
                statement = f'DELETE FROM {table} WHERE {" AND ".join(map(lambda c: f"{c} = %s", primary_key))}'
                cursor.execute(statement, key_value)
                db.commit()
            else:
                statement = f'DELETE FROM {table} WHERE {primary_key} = %s'
                cursor.execute(statement, (key_value,))
                db.commit()
        finally:
            cursor.close()
            db.close()
