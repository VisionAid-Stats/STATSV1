import cherrypy
import cherrypy_cors

import Database


class Student():
    def __init__(self, db=Database.Database()):
        self.db = db
        self.valid_columns = {'email', 'name', 'age', 'gender', 'visual_acuity', 'mobile', 'whatsapp', 'education_qual',
                              'address', 'education_detail', 'mother_tongue', 'education_tongue', 'employment_details',
                              'computer_experience', 'expectations', 'share_permission', 'bank_account',
                              'learning_objectives', 'visual_impairment', 'usable_vision', 'pct_vision_loss',
                              'hear_about'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_all(self):
        students = self.db.execute_select(statement="SELECT * from student")
        return students

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_by_id(self, student_id):
        student = self.db.execute_select(
            statement='SELECT * from student WHERE student_id = %s',
            params=(student_id,)
        )
        return student

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_by_name(self, name):
        student = self.db.execute_select(
            statement='SELECT * from student WHERE name = %s',
            params=(name,)
        )
        return student

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
            self.db.execute_insert(table='student', columns=columns, values=values)
            return {'success': True}
