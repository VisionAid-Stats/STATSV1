import cherrypy

import Database


class CourseOffering:
    def __init__(self, db=Database.Database()):
        self.db = db
        self.valid_columns = {'course_id', 'pm_user_id', 'trainer_id', 'centre_id', 'mode', 'start_date', 'end_date',
                              'frequency', 'duration', 'deposit', 'max_students'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_all(self):
        offerings = self.db.execute_select(
            statement="""
                SELECT 
                    o.course_offering_id,
                    o.start_date,
                    o.course_id,
                    c.name AS course_name,
                    c.code AS course_code,
                    o.trainer_id,
                    t.name AS trainer_name,
                    o.pm_user_id,
                    u.name AS pm_name,
                    o.centre_id,
                    ce.location AS centre_location
                FROM course_offering o
                JOIN course c ON c.course_id = o.course_id
                JOIN user u ON u.user_id = o.pm_user_id
                JOIN trainer t ON t.trainer_id = o.trainer_id
                JOIN centre ce ON ce.centre_id = o.centre_id
            """
        )
        for o in offerings:
            o['start_date'] = str(o['start_date'])
        return offerings

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def create(self):
        columns = []
        values = []
        data = cherrypy.request.json
        for col in data:
            if col not in self.valid_columns:
                return {'error': 'invalid column "%s"' % col}
            columns.append(col)
            values.append(data[col])
        self.db.execute_insert(table='course_offering', columns=columns, values=values)
        return {}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def add_student(self):
        data = cherrypy.request.json
        if 'course_offering_id' not in data:
            return {'error': 'missing "course_offering_id"'}
        if 'student_id' not in data:
            return {'error': 'missing "student_id"'}
        self.db.execute_insert(
            table='course_offering_link_student',
            columns=('course_offering_id', 'student_id'),
            values=(data['course_offering_id'], data['student_id']))
        return {'success': True}
