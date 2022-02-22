import cherrypy

import Database


class Course:
    def __init__(self, db=Database.Database()):
        self.db = db

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_all(self):
        courses = self.db.execute_select(statement="SELECT * FROM course")
        return courses

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_by_code(self, code):
        courses = self.db.execute_select(
            statement="SELECT * FROM course WHERE code = %s",
            params=(code,)
        )
        return courses

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_by_id(self, course_id):
        courses = self.db.execute_select(
            statement="SELECT * FROM course WHERE course_id = %s",
            params=(course_id,)
        )
        return courses
