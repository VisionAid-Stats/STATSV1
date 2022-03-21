import cherrypy
import cherrypy_cors

import Database


class Trainer:
    def __init__(self, db=Database.Database()):
        self.db = db
        self.valid_columns = {'name', 'email', 'location'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_all(self):
        trainers = self.db.execute_select(statement="SELECT * from trainer")
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
                        'error': 'invalid column "%s"; must be one of: %s' % (col, str(self.valid_columns))
                    }
                columns.append(col)
                values.append(data[col])
            self.db.execute_insert(table='trainer', columns=columns, values=values)
            return {'success': True}
