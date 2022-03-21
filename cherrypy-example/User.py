import hashlib

import cherrypy
import cherrypy_cors
import jwt

import Database


class User:
    def __init__(self, db=Database.Database()):
        self.db = db
        self.valid_columns = ['email', 'name', 'password', 'is_pm', 'is_admin']

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_all(self):
        users = self.db.execute_select(statement="SELECT user_id,name,email,is_admin,is_pm,enabled from user")
        return users

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_by_id(self, user_id):
        user = self.db.execute_select(
            statement='SELECT user_id,name,email,is_admin,is_pm,enabled from user WHERE user_id = %s',
            params=(user_id,))
        return user

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_pms(self):
        user = self.db.execute_select(
            statement='SELECT user_id,name,email,is_admin,is_pm,enabled from user WHERE is_pm = 1 AND enabled = 1')
        return user

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def login(self, email, password):
        user = self.db.execute_select(
            statement='''SELECT user_id, name, email, is_admin, is_pm from user
                         WHERE enabled = 1 AND email = %s AND password = sha2(%s, 512)''',
            params=(email, password))
        if len(user) == 0:
            return {'success': False, 'error': 'Login failed, invalid email address and/or password.'}
        if len(user) > 1:
            return {'success': False, 'error': 'Fatal error, please contact an administrator'}
        return {'success': True, 'token': jwt.encode(user[0], 'Vi$i0nAid', algorithm='HS512')}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def create(self):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy_cors.preflight(allowed_methods=['POST'])
        else:
            data = cherrypy.request.json
            columns = list(self.valid_columns)
            values = []
            for col in columns:
                if col not in data:
                    return {'success': False, 'error': 'Required column %s is missing.' % col}
                if col == 'password':
                    values.append(hashlib.sha512(data[col].encode('UTF-8')).hexdigest())
                else:
                    values.append(data[col])
            user = self.db.execute_select(statement='SELECT * FROM user WHERE email = %s', params=(data['email'],))
            if len(user) != 0:
                return {'success': False, 'error': 'A user with this email address already exists.'}
            self.db.execute_insert(table='user', columns=columns, values=values)
            return {'success': True}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def update(self):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy_cors.preflight(allowed_methods=['PUT'])
        else:
            data = cherrypy.request.json
            if 'user_id' not in data:
                return {'success': False, 'error': 'Required column user_id missing'}
            if 'email' in data:
                user = self.db.execute_select(statement='SELECT user_id FROM user WHERE email = %s',
                                              params=(data['email'],))
                if len(user) > 1 or str(user[0]['user_id']) != str(data['user_id']):
                    return {'success': False, 'error': 'A different user with this email address already exists.'}
            where = 'user_id = %s' % data['user_id']
            columns = []
            values = []
            for col in data:
                if col == 'user_id':
                    continue
                if col not in self.valid_columns:
                    return {
                        'success': False,
                        'error': 'invalid column "%s"; must be one of: %s' % (col, str(self.valid_columns))
                    }
                columns.append(col)
                if col == 'password':
                    values.append(hashlib.sha512(data[col].encode('UTF-8')).hexdigest())
                else:
                    values.append(data[col])
            self.db.execute_update(table='user', columns=columns, values=values, where=where)
            return {'success': True}
