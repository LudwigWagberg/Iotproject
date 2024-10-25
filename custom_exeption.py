class TemperatureOutOfRangeExeption(Exception):
    def __init__(self, temperature, message = "Temperature is out of range:"):
        self.temperature = temperature
        self.message = f"{message} {temperature}°C:"
        super().__init__(self.message)

class BatteryOutOfRangeException(Exception):
    def __init__(self, battery, message = "Battery is out of range:"):
        self.battery = battery 
        self.message = f"{message} {battery}"
        super().__init__(self.message)

class SensorDataNotFoundException(Exception):
    def __init__(self, message="Sensor data not found"):
        self.message = message
        super().__init__(self.message)
