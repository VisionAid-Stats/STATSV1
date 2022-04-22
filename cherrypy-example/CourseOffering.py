import cherrypy
import cherrypy_cors
import re

import Database


class CourseOffering:
    def __init__(self, db=Database.Database()):
        self.db = db
        self.valid_columns = {'course_id', 'pm_user_id', 'trainer_id', 'centre_id', 'mode', 'start_date', 'end_date',
                              'frequency', 'duration', 'deposit', 'max_students'}
        self.required_columns = {'course_id', 'pm_user_id', 'start_date'}
        self.checklist_regex = re.compile(r'item_\d{1,2}_(completion|remarks)')
        self.year_regex = re.compile(r'\d{2}(\d{2})-\d{2}-\d{2}')

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_all(self):
        offerings = self.db.execute_select(
            statement="""
                SELECT 
                    o.course_offering_id,
                    o.start_date,
                    o.course_id,
                    o.batch,
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
        if cherrypy.request.method == 'OPTIONS':
            cherrypy_cors.preflight(allowed_methods=['POST'])
        else:
            columns = []
            values = []
            data = cherrypy.request.json
            for col in self.required_columns:
                if col not in data:
                    return {'success': False, 'error': f'Required column "{col}" not present'}
            for col in data:
                if col not in self.valid_columns:
                    return {
                        'success': False,
                        'error': f'invalid column "{col}"; must be one of: {str(self.valid_columns)}'
                    }
                columns.append(col)
                values.append(data[col])

            # Get batch number
            match = self.year_regex.match(data['start_date'])
            if not match:
                return {'success': False, 'error': 'No start_date provided or invalid format (expected YYYY-MM-DD)'}
            yy = match.group(1)
            statement = '''
                SELECT COUNT(*) AS count
                FROM course_offering
                WHERE course_id = %s
                AND start_date >= %s
                AND start_date <= %s
            '''
            params = (data['course_id'], f'20{yy}-01-01', f'20{yy}-12-31')
            count = self.db.execute_select(statement=statement, params=params)[0]['count']
            batch = f'{count + 1}-{match.group(1)}'
            columns.append('batch')
            values.append(batch)

            course_offering_id = self.db.execute_insert(table='course_offering', columns=columns, values=values)
            self.db.execute_insert(
                table='course_offering_checklist',
                columns=('course_offering_id',),
                values=(course_offering_id,))
            return {'success': True, 'course_offering_id': course_offering_id}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def update(self):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy_cors.preflight(allowed_methods=['PUT'])
        else:
            data = cherrypy.request.json
            if 'course_offering_id' not in data:
                return {'success': False, 'error': 'Required column course_offering_id missing'}
            columns = []
            values = []
            for col in data:
                if col == 'course_offering_id':
                    continue
                if col not in self.valid_columns:
                    return {
                        'success': False,
                        'error': f'invalid column "{col}"; must be one of: {str(self.valid_columns)}'
                    }
                columns.append(col)
                values.append(data[col])
            where = f'course_offering_id = {data["course_offering_id"]}'
            self.db.execute_update(table='course_offering', columns=columns, values=values, where=where)
            return {'success': True}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def delete(self, course_offering_id):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy_cors.preflight(allowed_methods=['DELETE'])
        else:
            self.db.execute_delete(table='course_offering', primary_key='centre_id', key_value=course_offering_id)
            return {'success': True}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def add_student(self):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy_cors.preflight(allowed_methods=['POST'])
        else:
            data = cherrypy.request.json
            if 'course_offering_id' not in data:
                return {'success': False, 'error': 'missing "course_offering_id"'}
            if 'student_id' not in data:
                return {'success': False, 'error': 'missing "student_id"'}
            self.db.execute_insert(
                table='course_offering_link_student',
                columns=('course_offering_id', 'student_id'),
                values=(data['course_offering_id'], data['student_id']))
            return {'success': True}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def remove_student(self):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy_cors.preflight(allowed_methods=['POST'])
        else:
            data = cherrypy.request.json
            if 'course_offering_id' not in data:
                return {'success': False, 'error': 'missing "course_offering_id"'}
            if 'student_id' not in data:
                return {'success': False, 'error': 'missing "student_id"'}
            self.db.execute_delete(
                table='course_offering_link_student',
                primary_key=('course_offering_id', 'student_id'),
                key_value=(data['course_offering_id'], data['student_id']))

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_by_id(self, course_offering_id):
        statement = """
                    SELECT 
                        o.course_offering_id,
                        o.start_date,
                        o.course_id,
                        o.batch,
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
                    WHERE o.course_offering_id = %s
                    """
        offering = self.db.execute_select(statement=statement, params=(course_offering_id,))
        if len(offering) > 0:
            offering[0]['start_date'] = str(offering[0]['start_date'])
        return offering

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_by_pm(self, pm_user_id):
        statement = """
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
                    WHERE o.pm_user_id = %s
                    """
        offerings = self.db.execute_select(statement=statement, params=(pm_user_id,))
        for o in offerings:
            o['start_date'] = str(o['start_date'])
        return offerings

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_students(self, course_offering_id):
        statement = '''
                    SELECT s.*
                    FROM course_offering_link_student l
                    JOIN student s ON s.student_id = l.student_id
                    WHERE l.course_offering_id = %s;
                    '''
        students = self.db.execute_select(statement=statement, params=(course_offering_id,))
        return students

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_checklist(self, course_offering_id):
        statement = 'SELECT * FROM course_offering_checklist WHERE course_offering_id = %s'
        checklist = self.db.execute_select(statement=statement, params=(course_offering_id,))
        return checklist[0]

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def update_checklist(self):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy_cors.preflight(allowed_methods=['PUT'])
        else:
            data = cherrypy.request.json
            columns = []
            values = []
            if 'course_offering_id' not in data:
                return {
                    'success': False,
                    'error': 'course_offering_id is required'
                }
            where = f'course_offering_id = {data["course_offering_id"]}'
            for col in data:
                if col == 'course_offering_id':
                    continue
                if not self.checklist_regex.match(col):
                    return {
                        'success': False,
                        'error': 'column name must be item_N_completion or item_N_remarks where N is between 1 and 15'
                    }
                columns.append(col)
                values.append(data[col])
            self.db.execute_update(table='course_offering', columns=columns, values=values, where=where)
            return {'success': True}

    # @cherrypy.expose
    # @cherrypy.tools.json_in()
    # @cherrypy.tools.json_out()
    # def close(self):
    #     if cherrypy.request.method == 'OPTIONS':
    #         cherrypy_cors.preflight(allowed_methods=['POST'])
    #     else:
    #         data = cherrypy.request.json
    #         if 'course_offering_id' not in data:
    #             return {
    #                 'success': False,
    #                 'error': 'course_offering_id required'
    #             }
    #         if 'graduated_student_ids' not in data:
    #             return {
    #                 'success': False,
    #                 'error': 'graduated_student_ids array required'
    #             }
