import cherrypy
import cherrypy_cors

import Database
from CourseOffering import CourseOffering
from Trainer import Trainer
from User import User
from Student import Student
from Course import Course
from Centre import Centre

if __name__ == '__main__':
    db = Database.Database()
    cherrypy_cors.install()
    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        # 'server.socket_port': '8081',
        'cors.expose.on': True
    })
    cherrypy.tree.mount(User(db=db), '/user')
    cherrypy.tree.mount(Student(db=db), '/student')
    cherrypy.tree.mount(Course(db=db), '/course')
    cherrypy.tree.mount(Trainer(db=db), '/trainer')
    cherrypy.tree.mount(CourseOffering(db=db), '/course_offering')
    cherrypy.tree.mount(Centre(db=db), '/centre')
    cherrypy.engine.start()
    cherrypy.engine.block()
    db.close()
