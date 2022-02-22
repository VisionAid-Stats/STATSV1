import cherrypy

import Database


class Student():
    def __init__(self, db=Database.Database()):
        self.db = db

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
