from configobj import ConfigObj
from flask.ext.socketio import emit
from flask import Blueprint, render_template, url_for, copy_current_request_context, jsonify, g, request
from threading import Thread, Event
from classes import TemperatureController, Heater, Sensor, PID
from models import Recipe
from PiBrew import socketio

recipes = Blueprint('recipes', __name__, template_folder='templates')

global socketio, temperatures, temperature_sensor, heat_engine, temperature_controller, pid, params

#random number Generator Thread
thread = Thread()
thread_stop_event = Event()


temperatures = []
temperature_controller = Thread()
params = ConfigObj(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')).dict()



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
    print "Brew clicked"
    recipe = Recipe.get()
    print recipe
