import cherrypy
import cherrypy_cors

import Database


class Centre:
    def __init__(self, db=Database.Database()):
        self.db = db
        self.valid_columns = {'name', 'email', 'location'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_all(self):
        centres = self.db.execute_select(statement="SELECT * from centre")
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
                    return {'error': 'invalid column "%s"; must be one of: %s' % (col, str(self.valid_columns))}
                columns.append(col)
                values.append(data[col])
            self.db.execute_insert(table='centre', columns=columns, values=values)
            return {'success': True}
