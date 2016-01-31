import sys
import abc
import ds18b20



class NoDeviceDetected: pass

class Sensor(object):
    "Meta-class implementing a temperature sensor interface"

    __metaclass__ = abc.ABCMeta
    error_read = -100.0

    def __init__(self):
        self._sensor = self.initialize_sensor()

    @abs.abstractmethod
    def initialize_sensor(self):
        """Function that initializes sensor
        """
        pass

    @abc.abstractmethod
    def read_temperature(self, unit='celsius'):
        """Read temperature from the sensor

        :param unit: unit to get. can be celsius or farenheit
        :returns float: temperature

        """
        pass

def DS18B20Sensor(Sensor):

    def initialize_sensor(self):
        try:
            sensor = ds18b20.DS18B20()
            return sensor
        except Exception:
            raise NoDeviceDetected('Cannot detect DS18B20 device!')

    def read_temperature(self, unit='celsius'):
        if unit.lower() == 'celsius' or unit.lower().startswith('c'):
            try:
                return self.sensor.get_temperature(unit=1)
            except Exception:
                sys.stderr.write("Temperature read error!\n")
                return self.error_read
        elif unit.lower() == 'fahrenheit' or unit.lower().startswith('f'):
            try:
                return self.sensor.get_temperature(unit=2)
            except Exception:
                sys.stderr.write("Temperature read error!\n")
                return self.error_read
        else:
            raise Exception("Bad units: can be celsius or fahrenheit (C/F)")
