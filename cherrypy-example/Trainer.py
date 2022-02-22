import cherrypy

import Database


class Trainer:
    def __init__(self, db=Database.Database()):
        self.db = db

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
