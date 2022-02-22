import cherrypy

import Database
from CourseOffering import CourseOffering
from Trainer import Trainer
from User import User
from Student import Student
from Course import Course

cherrypy.server.socket_host = '0.0.0.0'
#cherrypy.config.update({'server.socket_port': 80})
cherrypy.engine.restart()

if __name__ == '__main__':
    db = Database.Database()
    cherrypy.tree.mount(User(db=db), '/user')
    cherrypy.tree.mount(Student(db=db), '/student')
    cherrypy.tree.mount(Course(db=db), '/course')
    cherrypy.tree.mount(Trainer(db=db), '/trainer')
    cherrypy.tree.mount(CourseOffering(db=db), '/course_offering')
    cherrypy.engine.start()
    cherrypy.engine.block()
    db.close()
