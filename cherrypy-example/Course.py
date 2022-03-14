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
                    return {'error': 'invalid column "%s"; must be one of: %s' % (col, str(self.valid_columns))}
                columns.append(col)
                values.append(data[col])
            self.db.execute_insert(table='course', columns=columns, values=values)
            return {'success': True}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def interests(self, course=None):
        statement = '''SELECT i.student_id,
                              i.course_id,
                              s.name as student_name,
                              c.code as course_code,
                              c.name as course_name
                       FROM   student_link_course_interest i,
                              student s,
                              course c
                       WHERE i.student_id = s.student_id
                         AND i.course_id = c.course_id'''
        if course is None:
            interests = self.db.execute_select(statement=statement)
        else:
            statement += ' AND (c.course_id = %s OR c.code = %s)'
            interests = self.db.execute_select(statement=statement, params=(course, course))

        return interests
