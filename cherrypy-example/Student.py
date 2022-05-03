import cherrypy
import cherrypy_cors
from mysql.connector import IntegrityError

import Database


class Student():
    def __init__(self, db=Database.Database()):
        self.db = db
        self.valid_columns = {'email', 'name', 'age', 'gender', 'visual_acuity', 'mobile', 'whatsapp', 'education_qual',
                              'address', 'education_detail', 'mother_tongue', 'education_tongue', 'employment_details',
                              'computer_experience', 'expectations', 'share_permission', 'bank_account',
                              'learning_objectives', 'visual_impairment', 'usable_vision', 'pct_vision_loss',
                              'hear_about', 'sharepoint_url'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_all(self, order='student_id'):
        if order != 'student_id' and order not in self.valid_columns:
            return {'success': False, 'error': f'order must be one of: {", ".join(self.valid_columns)}'}
        students = self.db.execute_select(statement="SELECT * from student ORDER BY %s DESC", params=(order,))
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
    @cherrypy.tools.json_out()
    def get_by_email(self, email):
        student = self.db.execute_select(
            statement='SELECT * from student WHERE email = %s',
            params=(email,)
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
                    return {
                        'success': False,
                        'error': f'invalid column "{col}"; must be one of: {str(self.valid_columns)}'
                    }
                columns.append(col)
                values.append(data[col])
            student = self.db.execute_select(
                statement='SELECT * FROM student WHERE email = %s OR mobile = %s',
                params=(data['email'], data['mobile'])
            )
            if len(student) != 0:
                return {
                    'success': False,
                    'error': 'A student record with this email address or mobile number already exists. Please contact VisionAid at info@visionaid.org to update your records.'
                }
            student_id = self.db.execute_insert(table='student', columns=columns, values=values)
            return {'success': True, 'student_id': student_id}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def update(self):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy_cors.preflight(allowed_methods=['PUT'])
        else:
            data = cherrypy.request.json
            if 'student_id' not in data:
                return {'success': False, 'error': 'Required column student_id missing'}
            columns = []
            values = []
            for col in data:
                if col == 'student_id':
                    continue
                if col not in self.valid_columns:
                    return {
                        'success': False,
                        'error': f'invalid column "{col}"; must be one of: {str(self.valid_columns)}'
                    }
                columns.append(col)
                values.append(data[col])
            where = f'student_id = {data["student_id"]}'
            self.db.execute_update(table='student', columns=columns, values=values, where=where)
            return {'success': True}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def delete(self, student_id):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy_cors.preflight(allowed_methods=['DELETE'])
        else:
            self.db.execute_delete(table='student', primary_key='student_id', key_value=student_id)
            return {'success': True}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def add_interests(self):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy_cors.preflight(allowed_methods=['POST'])
        else:
            data = cherrypy.request.json
            if 'student_id' not in data:
                return {'success': False, 'error': 'Required column student_id missing'}
            if 'course_ids' not in data:
                return {'success': False, 'error': 'Required array course_ids missing'}
            added = []
            failed = []
            # TODO: Add check for valid course/student ids
            for cid in data['course_ids']:
                try:
                    self.db.execute_insert(
                        table='student_link_course_interest',
                        columns=('student_id', 'course_id'),
                        values=(data['student_id'], cid)
                    )
                    added.append(cid)
                except IntegrityError:
                    failed.append(cid)
            return {'success': True, 'added': added, 'duplicates': failed}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def languages(self):
        languages = self.db.execute_select(statement='SELECT * FROM languages ORDER BY language')
        return languages

    def enrollments(self, student_id=None):
        statement = '''
                    SELECT
                        s.name AS student_name,
                        c.name AS course_name,
                        c.code AS course_code,
                        o.batch AS course_batch,
                        o.start_date,
                        NOT o.complete AS in_progress,
                        l.graduated,
                        s.student_id,
                        l.course_offering_id
                    FROM course_offering_link_student l
                    JOIN course_offering o
                        ON o.course_offering_id = l.course_offering_id
                    JOIN course c
                        ON c.course_id = o.course_id
                    JOIN student s
                        ON s.student_id = l.student_id
                    '''
        if student_id is not None:
            statement += f' WHERE student_id = {student_id}'
        statement += 'ORDER BY student_name ASC, course_offering_id DESC'
        enrollments = self.db.execute_select(statement=statement)
        for e in enrollments:
            e['start_date'] = str(e['start_date'])
        return enrollments
