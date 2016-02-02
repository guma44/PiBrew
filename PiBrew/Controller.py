import threading
from flask.ext.socketio import emit
import time
import random
import RPi.GPIO as GPIO
#
global temp_for_sensor
temp_for_sensor = 20.0

class Sensor:
    "Class implementing temperature sensor"
    def read_temperature(self):
        return round(random.uniform(temp_for_sensor - 0.5, temp_for_sensor + 0.5), 2)

class Timer:
    def __init__(self):
        self.start_time = None

    def start(self):
        self.start_time = time.time()

    def elapsed(self, how='minutes'):
        if how == 'minutes':
            return (time.time() - self.start_time)/60.0
        else:
            return time.time() - self.start_time

    def is_on(self):
        if self.start_time is None:
            return False
        else:
            return True

class RecipeManager:
    def __init__(self, recipe):
        self.recipe = recipe
        self.steps = recipe.steps
        self.nsteps = len(self.steps)

    def start(self):
        self.timer = Timer()
        self.timer.start()
        self.step_number = 0
        self.step_timer = Timer()
        self.current_step = self.steps[0]
        self.button_enabled = False

    def next_step(self):
        if self.step_number + 1 >= self.nsteps:
            return False
        else:
            self.step_number += 1
            self.current_step = self.steps[self.step_number]
            self.step_timer = Timer()
            self.button_enabled = False
            return True


class Heater:
    """Class that governs the heating process with GPIO"""
    def __init__(self, pin_number):
        if pin_number > 0:
            self.pin_number = pin_number
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(pin_number, GPIO.OUT)

    def heat(self, cycle_time, duty_cycle):
        if duty_cycle == 0:
            GPIO.output(self.pin_number, 0)
            print "No heating"
            time.sleep(cycle_time)
        elif duty_cycle == 100:
            GPIO.output(self.pin_number, 1)
            print "Heating 100"
            time.sleep(cycle_time)
        else:
            on_time, off_time = self.get_on_off_time(cycle_time, duty_cycle)
            print "Heating ", duty_cycle
            GPIO.output(self.pin_number, 1)
            time.sleep(on_time)
            GPIO.output(self.pin_number, 0)
            time.sleep(off_time)
    # def heat(self, cycle_time, duty_cycle):
    #     global temp_for_sensor
    #     if duty_cycle == 0:
    #         print "No heating"
    #         time.sleep(cycle_time)
    #     elif duty_cycle == 100:
    #         print "Heating 100%"
    #         if temp_for_sensor <= 100:
    #             temp_for_sensor += 2
    #         else:
    #             temp_for_sensor = 100.0
    #         time.sleep(cycle_time)
    #     else:
    #         print "Heating"
    #         if temp_for_sensor <= 100:
    #             temp_for_sensor += 2
    #         else:
    #             temp_for_sensor = 100.0
    #         time.sleep(cycle_time)

    def get_on_off_time(self, ct, dt):
        power = dt/100.0 # duty is in percent
        on_time = ct*(power)
        off_time = ct*(1.0 - power)
        return (on_time, off_time)


class TemperatureController(threading.Thread):
    """Class implements temperature controller that runs in the
    background.
    """

    def __init__(self, socketio, sensor, pid, heater, params):
        super(TemperatureController, self).__init__()
        self.socketio = socketio
        self.sensor = sensor
        self.pid = pid
        self.heater = heater
        self.params = params
        self._stop = threading.Event()
        self.mode = None
        self.recipe = None
        self.namespace = '/test'
        self.continue_clicked = False

    # Signals
    def emit_current_temperature(self, temp):
        self.socketio.emit('current_temperature', {'temperature': temp}, namespace=self.namespace)

    def emit_current_power(self, power):
        self.socketio.emit('current_power', {'power': power}, namespace=self.namespace)

    def emit_current_step(self, step):
        if step == "None":
            self.socketio.emit('current_step', {'step': "None", 'set_temp': "None"}, namespace=self.namespace)
        else:
            self.socketio.emit('current_step', {'step': step.name, 'set_temp': step.temperature}, namespace=self.namespace)

    def emit_current_recipe(self, recipe):
        self.socketio.emit('current_recipe', {'recipe': recipe}, namespace=self.namespace)

    def emit_remaining_time(self, t):
        if t <= 0:
            self.socketio.emit('remaining_time', {'remaining_time': 'Waiting for input...'}, namespace=self.namespace)
        else:
            mins, secs = divmod(t, 60)
            timeformat = '{:02d}:{:02d}'.format(int(mins), int(secs))
            self.socketio.emit('remaining_time', {'remaining_time': timeformat}, namespace=self.namespace)

    def enable_continue_button(self):
        self.socketio.emit('enable_continue_button', namespace=self.namespace)

    def disable_continue_button(self):
        self.socketio.emit('disable_continue_button', namespace=self.namespace)

    # Setters
    def set_target_temperature(self, temp):
        self.target_temperature = temp

    def set_mode(self, mode):
        self.mode = mode

    def set_recipe(self, recipe):
        self.recipe = RecipeManager(recipe)

    def set_continue_clicked(self):
        self.continue_clicked = True

    def start_recipe(self, recipe):
        self.data = {}
        self.set_recipe(recipe)
        self.recipe.start()
        self.set_mode('recipe')

    def stop_recipe(self):
        self.data = None
        self.recipe = None
        self.set_mode('off')
        self.continue_clicked = False
        self.disable_continue_button()
        self.emit_current_recipe("None")
        self.emit_current_step("None")
        self.socketio.emit('remaining_time', {'remaining_time': "None"}, namespace=self.namespace)

    def run(self):
        while not self.is_stopped():
            self.current_temperature = self.sensor.read_temperature()
            if self.mode == 'recipe':
                self.emit_current_recipe(self.recipe.recipe.name)
                self.emit_current_step(self.recipe.current_step)
                time_elapsed = str(self.recipe.timer.elapsed())
                self.data[time_elapsed] = {'power': str(self.current_power),
                                           'temp': str(self.current_temperature),
                                           'set_temp': str(self.recipe.current_step.temperature)}
                self.socketio.emit('new_data_for_plot', {'time': time_elapsed,
                                                         'temp': self.current_temperature,
                                                         'power': self.current_power,
                                                         'set_temp': str(self.recipe.current_step.temperature)},
                                   namespace=self.namespace)
                temp_reached = self.current_temperature >= self.recipe.current_step.temperature
                print "Step name", self.recipe.current_step.name
                if temp_reached and not self.recipe.step_timer.is_on():
                    print "Starting timer for", self.recipe.current_step.name
                    self.recipe.step_timer.start()
                if self.recipe.step_timer.is_on():
                    if self.recipe.step_timer.elapsed() >= self.recipe.current_step.span and self.recipe.current_step.span > 0:
                        is_next_step = self.recipe.next_step()
                        print "%s time out" % self.recipe.current_step.name
                        if not is_next_step:
                            self.stop_recipe()
                    elif self.recipe.current_step.span <= 0:
                        if self.continue_clicked:
                            is_next_step = self.recipe.next_step()
                            print "continue_is_clicked"
                            if not is_next_step:
                                self.stop_recipe()
                            else:
                                self.continue_clicked = False
                                assert not self.recipe.button_enabled, 'Button should be disabled here'
                                self.disable_continue_button()
                        else:
                            if not self.recipe.button_enabled:
                                print "Button not enabled"
                                self.enable_continue_button()
                            self.current_power = self.pid.calcPID_reg4(self.current_temperature, self.recipe.current_step.temperature)
                            self.emit_current_temperature(self.current_temperature)
                            self.emit_current_power(self.current_power)
                            self.emit_remaining_time(-1)
                            self.heater.heat(int(self.params.cycle_time), self.current_power)
                            # self.heater.heat(int(self.params.cycle_time), 0) # TODO


                    else:
                        self.current_power = self.pid.calcPID_reg4(self.current_temperature, self.recipe.current_step.temperature)
                        self.emit_current_temperature(self.current_temperature)
                        self.emit_current_power(self.current_power)
                        self.emit_remaining_time((60*self.recipe.current_step.span) - self.recipe.step_timer.elapsed(how='seconds'))
                        self.heater.heat(int(self.params.cycle_time), self.current_power)
                        # self.heater.heat(int(self.params.cycle_time), 0) # TODO
                else:
                    self.current_power = self.pid.calcPID_reg4(self.current_temperature, self.recipe.current_step.temperature)
                    self.emit_current_temperature(self.current_temperature)
                    self.emit_current_power(self.current_power)
                    self.socketio.emit('remaining_time', {'remaining_time': "Waiting for temperature..."}, namespace=self.namespace)
                    self.heater.heat(int(self.params.cycle_time), self.current_power)
                    # self.heater.heat(int(self.params.cycle_time), 100) # TODO

            elif self.mode == 'manual':
                pass
            else:
                self.current_power = 0
                self.emit_current_temperature(self.current_temperature)
                self.emit_current_power(self.current_power)
                self.heater.heat(int(self.params.cycle_time), self.current_power)

    def log_temperature():
        pass

    def stop(self):
        print "PIDController was stopped!"
        self.set_mode('off')
        self._stop.set()

    def is_stopped(self):
        return self._stop.isSet()
