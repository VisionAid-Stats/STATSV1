import cherrypy
import cherrypy_cors

import Database


class Centre:
    def __init__(self, db=Database.Database()):
        self.db = db
        self.valid_columns = {'location'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_all(self):
        centres = self.db.execute_select(statement="SELECT * from centre WHERE enabled = 1 ORDER BY location")
        return centres

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_by_id(self, centre_id):
        centre = self.db.execute_select(
            statement='SELECT * from centre WHERE centre_id = %s',
            params=(centre_id,)
        )
        return centre

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
            self.db.execute_insert(table='centre', columns=columns, values=values)
            return {'success': True}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def update(self):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy_cors.preflight(allowed_methods=['PUT'])
        else:
            data = cherrypy.request.json
            if 'centre_id' not in data:
                return {'success': False, 'error': 'Required column centre_id missing'}
            columns = []
            values = []
            for col in data:
                if col == 'centre_id':
                    continue
                if col not in self.valid_columns:
                    return {
                        'success': False,
                        'error': f'invalid column "{col}"; must be one of: {str(self.valid_columns)}'
                    }
                columns.append(col)
                values.append(data[col])
            where = f'centre_id = {data["centre_id"]}'
            self.db.execute_update(table='centre', columns=columns, values=values, where=where)
            return {'success': True}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def disable(self, centre_id):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy_cors.preflight(allowed_methods=['DELETE'])
        else:
            self.db.execute_update(
                table='centre',
                columns=('enabled',),
                values=(0,),
                where=f'centre_id = {centre_id}')
            return {'success': True}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def enable(self, centre_id):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy_cors.preflight(allowed_methods=['DELETE'])
        else:
            self.db.execute_update(
                table='centre',
                columns=('enabled',),
                values=(1,),
                where=f'centre_id = {centre_id}')
            return {'success': True}
