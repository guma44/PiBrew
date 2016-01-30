class Sensor:
    "Class implementing temperature sensor"
    def read_temperature(self):
        return round(random.uniform(temp_for_sensor - 0.5, temp_for_sensor + 0.5), 2)
