import cherrypy
import cherrypy_cors
from os import path

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
    config = {
        'server.socket_host': '0.0.0.0',
        'cors.expose.on': True
    }
    if path.exists('cert.pem') and path.exists('key.pem'):
        config['server.ssl_module'] = 'builtin'
        config['server.ssl_certificate'] = '/home/ubuntu/cert.pem'
        config['server.ssl_private_key'] = '/home/ubuntu/key.pem'
        config['server.socket_port'] = 443
    cherrypy.config.update(config)
    cherrypy.tree.mount(User(db=db), '/user')
    cherrypy.tree.mount(Student(db=db), '/student')
    cherrypy.tree.mount(Course(db=db), '/course')
    cherrypy.tree.mount(Trainer(db=db), '/trainer')
    cherrypy.tree.mount(CourseOffering(db=db), '/course_offering')
    cherrypy.tree.mount(Centre(db=db), '/centre')
    cherrypy.engine.signal_handler.subscribe()
    cherrypy.engine.start()
    cherrypy.engine.block()
