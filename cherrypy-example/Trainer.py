import cherrypy
import cherrypy_cors

import Database


class Trainer:
    def __init__(self, db=Database.Database()):
        self.db = db
        self.valid_columns = {'name', 'email', 'location', 'qualifications', 'state'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_all(self):
        trainers = self.db.execute_select(statement="SELECT * from trainer WHERE enabled = 1 ORDER BY name")
        return trainers

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_by_id(self, trainer_id):
        trainer = self.db.execute_select(
            statement='SELECT * from trainer WHERE trainer_id = %s',
            params=(trainer_id,)
        )
        return trainer

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
            self.db.execute_insert(table='trainer', columns=columns, values=values)
            return {'success': True}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def update(self):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy_cors.preflight(allowed_methods=['PUT'])
        else:
            data = cherrypy.request.json
            if 'trainer_id' not in data:
                return {'success': False, 'error': 'Required column trainer_id missing'}
            columns = []
            values = []
            for col in data:
                if col == 'trainer_id':
                    continue
                if col not in self.valid_columns:
                    return {
                        'success': False,
                        'error': f'invalid column "{col}"; must be one of: {str(self.valid_columns)}'
                    }
                columns.append(col)
                values.append(data[col])
            where = f'trainer_id = {data["trainer_id"]}'
            self.db.execute_update(table='trainer', columns=columns, values=values, where=where)
            return {'success': True}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def disable(self, trainer_id):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy_cors.preflight(allowed_methods=['DELETE'])
        else:
            self.db.execute_update(
                table='trainer',
                columns=('enabled',),
                values=(0,),
                where=f'trainer_id = {trainer_id}')
            # self.db.execute_delete(table='trainer', primary_key='trainer_id', key_value=trainer_id)
            return {'success': True}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def enable(self, trainer_id):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy_cors.preflight(allowed_methods=['DELETE'])
        else:
            self.db.execute_update(
                table='trainer',
                columns=('enabled',),
                values=(1,),
                where=f'trainer_id = {trainer_id}')
            return {'success': True}

    def get_states(self):
        states = self.db.execute_select(statement='SELECT value from state ORDER BY value')
        return states
