"""
Demo Flask application to test the operation of Flask with socket.io
Aim is to create a webpage that is constantly updated with random numbers from a background python process.
30th May 2014
"""

# Start with a basic flask app webpage.
from flask.ext.socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context, jsonify, g, request
from random import randint
from time import sleep
import os
from configobj import ConfigObj
from threading import Thread, Event
from flask.ext.mongoengine import MongoEngine
from classes import TemperatureController, Heater, Sensor, PID
import datetime

global socketio, temperatures, temperature_sensor, heat_engine, temperature_controller, pid, params, db

app = Flask(__name__)
app.config["MONGODB_SETTINGS"] = {'DB': "brewpy"}
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True

#turn the flask app into a socketio app
socketio = SocketIO(app)

db = MongoEngine(app)

#random number Generator Thread
thread = Thread()
thread_stop_event = Event()


temperatures = []
temperature_controller = Thread()
params = ConfigObj(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')).dict()


class Step(db.EmbeddedDocument):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    name = db.StringField(max_length=255, required=True)
    span = db.IntField(required=True)
    temperature = db.FloatField(required=True)

    def __unicode__(self):
        return self.name

class Recipe(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    name = db.StringField(max_length=255, required=True)
    slug = db.StringField(max_length=255, required=True)
    steps = db.ListField(db.EmbeddedDocumentField('Step'))

    def get_absolute_url(self):
        return url_for('post', kwargs={"slug": self.slug})

    def __unicode__(self):
        return self.name

    meta = {
        'allow_inheritance': True,
        'indexes': ['-created_at', 'slug'],
        'ordering': ['-name']
     }


@app.route('/')
def index():
    #only by sending this page first will the client be connected to the socketio instance
    return render_template('index.html')

@socketio.on('connect', namespace='/test')
def on_connect():
    # need visibility of the global thread object
    print('Client connected')
    global temperature_controller
    global temperature_sensor
    global params
    global heat_engine
    global pid
    global socketio
    temperature_sensor = Sensor()
    heat_engine = Heater()
    pid = PID(int(params['cycle_time']),
              float(params['Kc']),
              float(params['Ti']),
              float(params['Td']))

    #Start the random number generator thread only if the thread has not been started before.
    if not temperature_controller.isAlive():
        print "Starting temperature controller"
        temperature_controller = TemperatureController(socketio,
                                                       temperature_sensor,
                                                       pid,
                                                       heat_engine,
                                                       params)
        temperature_controller.start()

@socketio.on('disconnect', namespace='/test')
def on_disconnect():
    print('Client disconnected')

@socketio.on('brew_clicked', namespace='/test')
def brew_click():
    global temperature_controller
    print "Brew clicked"
    recipe = Recipe.objects(name='test3').get()
    temperature_controller.start_recipe(recipe)


if __name__ == '__main__':
    socketio.run(app)
