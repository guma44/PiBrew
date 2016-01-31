"""
"""

# Start with a basic flask app webpage.
from flask.ext.socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context, jsonify, g, request, redirect
from random import randint
from time import sleep
import os
import settings as params
import utils
from threading import Thread, Event
from flask.ext.mongoengine import MongoEngine
from flask.ext.mongoengine.wtf import model_form

# classes usef or the controller
from .Controller import TemperatureController, Heater, Sensor
from .PID import PID

import datetime

global socketio, temperatures, temperature_sensor, heat_engine, temperature_controller, pid, db, params_path

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
params_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.py')

class Step(db.EmbeddedDocument):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    name = db.StringField(max_length=255, required=True)
    span = db.IntField(required=True)
    temperature = db.IntField(required=True)

    def __unicode__(self):
        return self.name

class Recipe(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    name = db.StringField(max_length=255, required=True, unique=True)
    slug = db.StringField(max_length=255, required=True, unique=True)
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

@app.route('/recipes')
def recipes():
    #only by sending this page first will the client be connected to the socketio instance
    recipes = list(Recipe.objects())
    return render_template('recipes.html', recipes=recipes)

@app.route('/settings', methods=('GET', 'POST'))
def settings():
    if request.method == 'POST':
        new_kc = request.form.get('Kc_param')
        new_ti = request.form.get('Ti_param')
        new_td = request.form.get('Td_param')
        new_cycle_time = request.form.get('cycle_time_param')
        params.Kc = new_kc
        params.Ti = new_ti
        params.Td = new_td
        params.cycle_time = new_cycle_time
        utils.save_config(params_path, params)
        return redirect(url_for('index'))
    else:
        return render_template('settings.html', params=params)



@app.route('/show/<string:recipe_slug>', methods=("GET", 'POST'))
def show(recipe_slug):
    print "I am in recipe detail"
    recipe = Recipe.objects(slug=recipe_slug).get()
    return render_template("recipe_details.html", recipe=recipe)

@app.route('/brew/<string:recipe_slug>', methods=("GET",))
def brew(recipe_slug):
    global temperature_controller
    recipe = Recipe.objects(slug=recipe_slug).get()
    temperature_controller.start_recipe(recipe)
    return redirect(url_for('index'))

@socketio.on('show_recipe', namespace='/recipes')
def show_recipe(msg):
    if msg['data']:
        print "%s recipe selected" % msg['data']
        print url_for('.show', recipe_slug=msg['data'])
        return redirect(url_for('.show', recipe_slug=msg['data']))
    else:
        print "No recipe selected"

@app.route('/delete/<string:recipe_slug>', methods=("GET", 'POST'))
def delete(recipe_slug):
    print "I am in recipe delete"
    recipe = Recipe.objects(slug=recipe_slug).get()
    recipe.delete()
    return redirect(url_for('recipes'))

@app.route('/new', methods=('GET', 'POST'))
def new_recipe():
    if request.method == 'POST':
        step_names = request.form.getlist('step_name')
        step_times = request.form.getlist('step_time')
        step_temps = request.form.getlist('step_temp')
        steps = []
        for name, time, temp in zip(step_names, step_times, step_temps):
            steps.append(Step(name=name, span=int(time), temperature=int(temp)))
        recipe = Recipe(name=request.form.get('recipe_name'),
                        slug=request.form.get('recipe_name').lower().replace(" ", "_"),
                        steps=steps)
        recipe.save()
        return redirect(url_for('recipes'))
    else:
        form = model_form(Recipe, exclude=('created_at'))(request.form)
        return render_template('new.html', form=form)

@app.route('/edit/<string:recipe_slug>', methods=('GET', 'POST'))
def edit_recipe(recipe_slug):
    if request.method == 'POST':
        step_names = request.form.getlist('step_name')
        step_times = request.form.getlist('step_time')
        step_temps = request.form.getlist('step_temp')
        steps = []
        for name, time, temp in zip(step_names, step_times, step_temps):
            steps.append(Step(name=name, span=int(time), temperature=int(temp)))
        recipe = Recipe(name=request.form.get('recipe_name'),
                        slug=request.form.get('recipe_name').lower().replace(" ", "_"),
                        steps=steps)
        print Recipe.objects()
        old_recipe = Recipe.objects(slug=recipe_slug).get()
        old_recipe.delete()
        recipe.save()
        return redirect(url_for('recipes'))
    else:
        recipe = Recipe.objects(slug=recipe_slug).get()
        return render_template('recipe_edit.html', recipe=recipe)


@socketio.on('connect', namespace='/test')
def on_connect():
    # need visibility of the global thread object
    print('Client connected')
    global temperature_controller
    global temperature_sensor
    global heat_engine
    global pid
    global socketio
    temperature_sensor = Sensor()
    heat_engine = Heater()
    pid = PID(params.cycle_time,
              params.Kc,
              params.Ti,
              params.Td)

    #Start the random number generator thread only if the thread has not been started before.
    if not temperature_controller.isAlive():
        print "Starting temperature controller"
        temperature_controller = TemperatureController(socketio,
                                                       temperature_sensor,
                                                       pid,
                                                       heat_engine,
                                                       params)
        temperature_controller.start()
    else:
        if temperature_controller.recipe is not None:
            if temperature_controller.recipe.button_enabled:
                emit('enable_continue_button', namespace='/test')
            if temperature_controller.data is not None:
                emit('data_for_plot', temperature_controller.data, namespace='/test')


@socketio.on('disconnect', namespace='/test')
def on_disconnect():
    print('Client disconnected')

@socketio.on('brew_clicked', namespace='/test')
def brew_click():
    global temperature_controller
    recipe = Recipe.objects(name='test3').get()
    temperature_controller.start_recipe(recipe)

@app.route('/stop', methods=("GET",))
def stop():
    global temperature_controller
    temperature_controller.stop_recipe()
    return redirect(url_for('index'))

@socketio.on('button_enabled', namespace='/test')
def enable_continue_button():
    global temperature_controller
    temperature_controller.recipe.button_enabled = True

@socketio.on('button_disabled', namespace='/test')
def disable_continue_button():
    global temperature_controller
    if temperature_controller.recipe is not None:
        temperature_controller.recipe.button_enabled = False

@socketio.on('continue_clicked', namespace='/test')
def continure_clicked():
    global temperature_controller
    temperature_controller.continue_clicked = True


if __name__ == '__main__':
    socketio.run(app)
