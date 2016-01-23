import threading
from flask.ext.socketio import emit
import time
from random import randint
# import RPi.GPIO as GPIO

class Sensor:
    "Class implementing temperature sensor"
    def read_temperature(self):
        return randint(0, 99)

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
    # def __init__(self, pin_number):
    #     if pin_number > 0:
    #         GPIO.setup(pin_number, GPIO.OUT)

    # def heat(cycle_time, duty_cycle):
    #     if duty_cycle == 0:
    #         GPIO.output(pin_number, 0)
    #         time.sleep(cycle_time)
    #     elif duty_cycle == 100:
    #         GPIO.output(pin_number, 1)
    #         time.sleep(cycle_time)
    #     else:
    #         on_time, off_time = self.get_on_off_time(cycle_time, duty_cycle)
    #         GPIO.output(pin_number, 1)
    #         time.sleep(on_time)
    #         GPIO.output(pin_number, 0)
    #         time.sleep(off_time)
    def heat(self, cycle_time, duty_cycle):
        print "Heating..."
        time.sleep(cycle_time)

    def get_on_off_time(self, ct, dt):
        power = duty_cycle/100.0 # duty is in percent
        on_time = cycle_time*(power)
        off_time = cycle_time*(1.0 - power)
        return (on_time, off_time)

# PIC controller class acting as a thread
class TemperatureController(threading.Thread):

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

    def emit_current_action(self, action):
        self.socketio.emit('current_action', {'action': action}, namespace=self.namespace)

    def emit_remaining_time(self, t):
        mins, secs = divmod(t, 60)
        timeformat = '{:02d}:{:02d}'.format(mins, secs)
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
        self.set_recipe(recipe)
        self.recipe.start()
        self.set_mode('recipe')

    def stop_recipe(self):
        self.recipe = None
        self.set_mode('off')
        self.continue_clicked = False
        self.disable_continue_button()

    def run(self):
        step_start_time = None
        while not self.is_stopped():
            current_temperature = self.sensor.read_temperature()
            if self.mode == 'recipe':
                temp_reached = current_temperature >= self.recipe.current_step.temperature
                print "Step name", self.recipe.current_step.name
                if temp_reached and not self.recipe.step_timer.is_on():
                    self.recipe.step_timer.start()
                if self.recipe.step_timer.is_on():
                    if self.recipe.step_timer.elapsed() >= self.recipe.current_step.span and self.recipe.current_step.span > -1:
                        is_next_step = self.recipe.next_step()
                        print "reached span"
                        if not is_next_step:
                            self.stop_recipe()
                    elif self.recipe.current_step.span <= -1:
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
                            #TODO this is just for thest
                            print "Im in -1"
                            current_power = randint(0, 50)
                            self.emit_current_temperature(current_temperature)
                            self.emit_current_power(current_power)
                            self.heater.heat(int(self.params['cycle_time']), current_power)


                    else:
                        #TODO this is just for thest
                        current_power = randint(0, 50)
                        self.emit_current_temperature(current_temperature)
                        self.emit_current_power(current_power)
                        self.heater.heat(int(self.params['cycle_time']), current_power)
                else:
                    current_power = randint(0, 50)
                    self.emit_current_temperature(current_temperature)
                    self.emit_current_power(current_power)
                    self.heater.heat(int(self.params['cycle_time']), current_power)

            elif self.mode == 'manual':
                pass
            else:
                current_power = randint(0, 50)
                self.emit_current_temperature(current_temperature)
                self.emit_current_power(current_power)
                self.heater.heat(int(self.params['cycle_time']), current_power)

    def activate_recipe_step():
        pass
    def log_temperature():
        pass
    def continue_clicked():
        pass
    def fulsh_csv_file():
        pass

    def stop(self):
        print "PIDController was stopped!"
        self.set_mode('off')
        self._stop.set()
    def is_stopped(self):
        return self._stop.isSet()


class PID:
    """PID implemented by steve71 at https://github.com/steve71/RasPiBrew/blob/master/RasPiBrew"""
    ek_1 = 0.0  # e[k-1] = SP[k-1] - PV[k-1] = Tset_hlt[k-1] - Thlt[k-1]
    ek_2 = 0.0  # e[k-2] = SP[k-2] - PV[k-2] = Tset_hlt[k-2] - Thlt[k-2]
    xk_1 = 0.0  # PV[k-1] = Thlt[k-1]
    xk_2 = 0.0  # PV[k-2] = Thlt[k-1]
    yk_1 = 0.0  # y[k-1] = Gamma[k-1]
    yk_2 = 0.0  # y[k-2] = Gamma[k-1]
    lpf_1 = 0.0 # lpf[k-1] = LPF output[k-1]
    lpf_2 = 0.0 # lpf[k-2] = LPF output[k-2]

    yk = 0.0 # output

    GMA_HLIM = 100.0
    GMA_LLIM = 0.0

    def __init__(self, ts, kc, ti, td):
        self.kc = kc
        self.ti = ti
        self.td = td
        self.ts = ts
        self.k_lpf = 0.0
        self.k0 = 0.0
        self.k1 = 0.0
        self.k2 = 0.0
        self.k3 = 0.0
        self.lpf1 = 0.0
        self.lpf2 = 0.0
        self.ts_ticks = 0
        self.pid_model = 3
        self.pp = 0.0
        self.pi = 0.0
        self.pd = 0.0
        if (self.ti == 0.0):
            self.k0 = 0.0
        else:
            self.k0 = self.kc * self.ts / self.ti
        self.k1 = self.kc * self.td / self.ts
        self.lpf1 = (2.0 * self.k_lpf - self.ts) / (2.0 * self.k_lpf + self.ts)
        self.lpf2 = self.ts / (2.0 * self.k_lpf + self.ts) 

    def calcPID_reg3(self, xk, tset, enable):
        ek = 0.0
        lpf = 0.0
        ek = tset - xk # calculate e[k] = SP[k] - PV[k]
        #--------------------------------------
        # Calculate Lowpass Filter for D-term
        #--------------------------------------
        lpf = self.lpf1 * pidpy.lpf_1 + self.lpf2 * (ek + pidpy.ek_1);

        if (enable):
            #-----------------------------------------------------------
            # Calculate PID controller:
            # y[k] = y[k-1] + kc*(e[k] - e[k-1] +
            # Ts*e[k]/Ti +
            # Td/Ts*(lpf[k] - 2*lpf[k-1] + lpf[k-2]))
            #-----------------------------------------------------------
            self.pp = self.kc * (ek - pidpy.ek_1) # y[k] = y[k-1] + Kc*(PV[k-1] - PV[k])
            self.pi = self.k0 * ek  # + Kc*Ts/Ti * e[k]
            self.pd = self.k1 * (lpf - 2.0 * pidpy.lpf_1 + pidpy.lpf_2)
            pidpy.yk += self.pp + self.pi + self.pd
        else:
            pidpy.yk = 0.0
            self.pp = 0.0
            self.pi = 0.0
            self.pd = 0.0

        pidpy.ek_1 = ek # e[k-1] = e[k]
        pidpy.lpf_2 = pidpy.lpf_1 # update stores for LPF
        pidpy.lpf_1 = lpf

        # limit y[k] to GMA_HLIM and GMA_LLIM
        if (pidpy.yk > pidpy.GMA_HLIM):
            pidpy.yk = pidpy.GMA_HLIM
        if (pidpy.yk < pidpy.GMA_LLIM):
            pidpy.yk = pidpy.GMA_LLIM

        return pidpy.yk

    def calcPID_reg4(self, xk, tset, enable):
        ek = 0.0
        ek = tset - xk # calculate e[k] = SP[k] - PV[k]

        if (enable):
            #-----------------------------------------------------------
            # Calculate PID controller:
            # y[k] = y[k-1] + kc*(PV[k-1] - PV[k] +
            # Ts*e[k]/Ti +
            # Td/Ts*(2*PV[k-1] - PV[k] - PV[k-2]))
            #-----------------------------------------------------------
            self.pp = self.kc * (pidpy.xk_1 - xk) # y[k] = y[k-1] + Kc*(PV[k-1] - PV[k])
            self.pi = self.k0 * ek  # + Kc*Ts/Ti * e[k]
            self.pd = self.k1 * (2.0 * pidpy.xk_1 - xk - pidpy.xk_2)
            pidpy.yk += self.pp + self.pi + self.pd
        else:
            pidpy.yk = 0.0
            self.pp = 0.0
            self.pi = 0.0
            self.pd = 0.0

        pidpy.xk_2 = pidpy.xk_1  # PV[k-2] = PV[k-1]
        pidpy.xk_1 = xk    # PV[k-1] = PV[k]

        # limit y[k] to GMA_HLIM and GMA_LLIM
        if (pidpy.yk > pidpy.GMA_HLIM):
            pidpy.yk = pidpy.GMA_HLIM
        if (pidpy.yk < pidpy.GMA_LLIM):
            pidpy.yk = pidpy.GMA_LLIM

        return pidpy.yk





