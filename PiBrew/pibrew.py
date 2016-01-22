"""
Demo Flask application to test the operation of Flask with socket.io
Aim is to create a webpage that is constantly updated with random numbers from a background python process.
30th May 2014
"""

# Start with a basic flask app webpage.
from flask.ext.socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context
from random import randint
from time import sleep
from threading import Thread, Event


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True

#turn the flask app into a socketio app
socketio = SocketIO(app)

#random number Generator Thread
thread = Thread()
thread_stop_event = Event()

global temperatures, temperature_thread, temperature_sensor

temperatures = []
temperature_monitor = Thread()

class Sensor:
    def read_temperature(self):
        return randint(0, 99)

class TemperatureMonitor(Thread):
    """
    Class implementing temperature monitor
    """
    def __init__(self, sensor):
        self.delay = 1
        self.sensor = sensor
        super(TemperatureMonitor, self).__init__()

    def get_temperature(self):
        while not thread_stop_event.isSet():
            temperature = self.sensor.read_temperature()
            socketio.emit('current_temperature', {'temperature': temperature},
                          namespace='/test')
            temperatures.append(temperature)
            sleep(self.delay)

    def run(self):
        self.get_temperature()


@app.route('/')
def index():
    #only by sending this page first will the client be connected to the socketio instance
    return render_template('index.html')

@socketio.on('connect', namespace='/test')
def on_connect():
    # need visibility of the global thread object
    print('Client connected')
    global temperature_monitor
    global temperature_sensor
    temperature_sensor = Sensor()

    #Start the random number generator thread only if the thread has not been started before.
    if not temperature_monitor.isAlive():
        print "Starting Thread"
        temperature_monitor = TemperatureMonitor(temperature_sensor)
        temperature_monitor.start()

@socketio.on('disconnect', namespace='/test')
def on_disconnect():
    print('Client disconnected')

@socketio.on('current_temperature', namespace='/test')
def print_number(message):
    print "I received:", message['data']


if __name__ == '__main__':
    socketio.run(app)
