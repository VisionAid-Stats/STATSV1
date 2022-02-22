import cherrypy
import Database


class User:
    def __init__(self, db=Database.Database()):
        self.db = db

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_all(self):
        users = self.db.execute_select(statement="SELECT user_id,name,email,is_admin,is_pm,enabled from user")
        return users

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_by_id(self, user_id):
        user = self.db.execute_select(
            statement='SELECT user_id,name,email,is_admin,is_pm,enabled from user WHERE user_id = %s',
            params=(user_id,))
        return user

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_pms(self):
        user = self.db.execute_select(
            statement='SELECT user_id,name,email,is_admin,is_pm,enabled from user WHERE is_pm = 1 AND enabled = 1')
        return user
