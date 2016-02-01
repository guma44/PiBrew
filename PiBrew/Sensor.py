import sys
import abc
import ds18b20



class NoDeviceDetected(Exception): pass

class Sensor(object):
    "Meta-class implementing a temperature sensor interface"

    __metaclass__ = abc.ABCMeta
    error_read = -100.0

    def __init__(self):
        self.sensor = self.initialize_sensor()

    @abc.abstractmethod
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

class DS18B20Sensor(Sensor):

    def __init__(self):
        Sensor.__init__(self)

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
            except Exception, e:
                sys.stderr.write("Temperature read error (%s)!\n" % (str(e)))
                return self.error_read
        elif unit.lower() == 'fahrenheit' or unit.lower().startswith('f'):
            try:
                return self.sensor.get_temperature(unit=2)
            except Exception, e:
                sys.stderr.write("Temperature read error (%s)!\n" % (str(e)))
                return self.error_read
        else:
            raise Exception("Bad units: can be celsius or fahrenheit (C/F)")
