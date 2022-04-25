import cherrypy
import cherrypy_cors

import Database


class Course:
    def __init__(self, db=Database.Database()):
        self.db = db
        self.valid_columns = {'code', 'name', 'is_online', 'is_offline'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_all(self):
        courses = self.db.execute_select(statement="SELECT * FROM course")
        return courses

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_by_code(self, code):
        courses = self.db.execute_select(
            statement="SELECT * FROM course WHERE code = %s",
            params=(code,)
        )
        return courses

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_by_id(self, course_id):
        courses = self.db.execute_select(
            statement="SELECT * FROM course WHERE course_id = %s",
            params=(course_id,)
        )
        return courses

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def create(self):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy_cors.preflight(allowed_methods=['POST'])
        else:
            columns = []
            values = []
            data = cherrypy.request.json
            for col in data:
                if col not in self.valid_columns:
                    return {
                        'success': False,
                        'error': f'invalid column "{col}"; must be one of: {str(self.valid_columns)}'
                    }
                columns.append(col)
                values.append(data[col])
            self.db.execute_insert(table='course', columns=columns, values=values)
            return {'success': True}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def update(self):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy_cors.preflight(allowed_methods=['PUT'])
        else:
            data = cherrypy.request.json
            if 'course_id' not in data:
                return {'success': False, 'error': 'Required column course_id missing'}
            if 'code' in data:
                course = self.db.execute_select(statement='SELECT course_id FROM course WHERE code = %s',
                                                params=(data['code'],))
                if len(course) > 1 or str(course[0]['course_id']) != str(data['course_id']):
                    return {'success': False, 'error': 'A different course with this code already exists.'}
            where = f'course_id = {data["course_id"]}'
            columns = []
            values = []
            for col in data:
                if col == 'course_id':
                    continue
                if col not in self.valid_columns:
                    return {
                        'success': False,
                        'error': 'invalid column "%s"; must be one of: %s' % (col, str(self.valid_columns))
                    }
                columns.append(col)
                values.append(data[col])
            self.db.execute_update(table='course', columns=columns, values=values, where=where)
            return {'success': True}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def disable(self, course_id):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy_cors.preflight(allowed_methods=['PUT'])
        else:
            self.db.execute_update(
                table='course',
                columns=('enabled',),
                values=(0,),
                where=f'course_id = {course_id}')
            # self.db.execute_delete(table='course', primary_key='course_id', key_value=course_id)
            return {'success': True}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def enable(self, course_id):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy_cors.preflight(allowed_methods=['PUT'])
        else:
            self.db.execute_update(
                table='course',
                columns=('enabled',),
                values=(1,),
                where=f'course_id = {course_id}')
            return {'success': True}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def interests(self, course=None, student_id=None):
        statement = '''SELECT i.student_id,
                              i.course_id,
                              s.name as student_name,
                              c.code as course_code,
                              c.name as course_name
                       FROM   student_link_course_interest i,
                              student s,
                              course c
                       WHERE  i.student_id = s.student_id
                         AND  i.course_id = c.course_id
                         AND  taken = 0'''
        if course is not None:
            statement += ' AND (c.course_id = %s OR c.code = %s)'
            interests = self.db.execute_select(statement=statement, params=(course, course))
        elif student_id is not None:
            statement += ' AND s.student_id = %s'
            interests = self.db.execute_select(statement=statement, params=(student_id,))
        else:
            interests = self.db.execute_select(statement=statement)
        return interests
