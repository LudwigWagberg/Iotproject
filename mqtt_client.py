import paho.mqtt.client as mqtt
import json
import requests
import threading
import logging
import os
from custom_exeption import TemperatureOutOfRangeExeption, BatteryOutOfRangeException, SensorDataNotFoundException
from exception_handler import handle_temperature_exeptions, handle_battery_exceptions, handle_noData_exceptions
from logger_config import setup_logger

setup_logger()

# Define the MQTT settings
BROKER_HOST ='172.18.0.40'
BROKER_PORT = 1883
TOPIC = 'TEMPERATURE'

# We take the username and password from system variables
USERNAME = os.getenv("MQTT_USERNAME", "default_user")
PASSWORD = os.getenv("MQTT_PASSWORD", "default_password")

# Define the API endpoint where data will be sent
API_URL = 'http://localhost:3000/temperature'

# This will run for 8 hours and then count + 1, when it reaches 3 it will proceed to other functions that will send an email
# THIS ONLY WORKS WITH ONE IOT-UNIT!!!!!! Need to add IMEI and other stuff
DATA_TIMEOUT = 15

# Grace perion initiation
MAX_MISSED_ATTEMPTS = 3
missed_data_count = 0
last_message_timer = None
timer_lock = threading.Lock()
 
# Reset the times when a message is recieved from the IoT
def reset_timer():
    global last_message_timer
    with timer_lock:
        if last_message_timer:
            last_message_timer.cancel()
        last_message_timer = threading.Timer(DATA_TIMEOUT, handle_data_timeout)
        last_message_timer.start()
        logging.debug("Timer reset.")
 
# Will be reached when nothing happens within the timer limit(8 h). Adds 1 to the missed_data_count and logs it.
# If the limit is reached it will throw an exception.
def handle_data_timeout():
    global missed_data_count
    with timer_lock:
        missed_data_count += 1
        logging.debug(f"Data timeout occurred. Missed attempts: {missed_data_count}")
 
    if missed_data_count < MAX_MISSED_ATTEMPTS:
        # Loggs a warning and prints a warning message
        logging.warning(f"Warning: No data received from the sensor. Attempt {missed_data_count} of {MAX_MISSED_ATTEMPTS}. Retrying...")
        print(f"Warning: No data received from the sensor. Attempt {missed_data_count} of {MAX_MISSED_ATTEMPTS}. Retrying...")
        reset_timer()  # Resets the timer
    else:
        try:
            # If we havn't received any data within 24 hours and gotten 3 warnings, we will throw an exception.
            raise SensorDataNotFoundException("No data received for the last 24 hours")
        except SensorDataNotFoundException as e:
            logging.error(e)
            print(e)
            handle_noData_exceptions(e)
        # Reset the missed_data_count to 0 and resets the timer
        missed_data_count = 0
        reset_timer()

# checks if given temperatures are within the acceptable range if not it throws an exception
# Throws the exception immediately, so if the first temperature value checked is outside the
# range the execution will stop. Meaning that you will only get an error for at most one temperature.
def check_temperature(temperature, source=""):
    if temperature < 1:
        raise TemperatureOutOfRangeExeption(f"Temperature to low in {source}: {temperature}")
    if temperature > 40:
        raise TemperatureOutOfRangeExeption(f"Temperature to high in {source}: {temperature}")
    return None 

def check_battery(battery, source=""):
    if battery <= 3.1:
        raise BatteryOutOfRangeException(f"Battery is at critical level in {source}: Battery level: {battery}")
    return None

def on_message(client, userdata, msg):
    global missed_data_count
    IMEI = None
    battery = None
    
    try:
        payload = msg.payload.decode('utf-8')
        json_payload = json.loads(payload)
        print(f"Message received on topic {msg.topic}: \n{json.dumps(json_payload, indent=4)}")

        # Transforms the json_payload into a new format and stores it in temperature_data.
        # Extracts specific fields like IMEI, Model, temperature readings, battery, and signal strength from the payload.
        # Initializes the 'timestamps' field as an empty dictionary, which will later store multiple timestamped readings.
        temperature_data = {
            "IMEI": json_payload.get("IMEI"),
            "Model": json_payload.get("Model"),
            "temperature1": json_payload.get("temperature1"),
            "temperature2": json_payload.get("temperature2"),
            "temperature3": json_payload.get("temperature3"),
            "battery": json_payload.get("battery"),
            "signal": json_payload.get("signal"),
            "timestamps": {}
        }
        
        IMEI = temperature_data.get("IMEI")
        battery = temperature_data.get("battery")
        
        # Loops through each key-value pair in json_payload.
        # Filters out keys that are numeric (e.g., timestamps) and have dictionary values.
        # For each numeric key (e.g. 1, 2), extracts the associated temperature readings and timestamp and stores them in temperature_data under 'timestamps'.
        for key, value in json_payload.items():
            if key.isdigit() and isinstance(value, dict):
                temperature_data["timestamps"][key] = {
                    "temperature1": value.get("temperature1"),
                    "temperature2": value.get("temperature2"),
                    "temperature3": value.get("temperature3"),
                    "timestamp": value.get("timestamp")
                }

                # goes thru all the temperature1's in the timestamps and sends the temperature to the check_temperature function with the timestamp key(e.g timestamp 1,timestamp 2)
                # If any of the temperatures are out of range, the check_temperature function will throw an exception, 
                temp_in_timestamp = float(value.get("temperature1", 0))
                check_temperature(temp_in_timestamp, source=f"timestamp {key}")
                
        battery = temperature_data.get("battery")
        check_battery(battery, source=f"IMEI {IMEI}")
                
        # Send data to the API if no temperature issues
        response = requests.post(API_URL, json=temperature_data)
        if response.status_code == 200:
            print("Data successfully sent to the API")
        else:
            print(f"Failed to send data to the API. Status code: {response.status_code}")

        with timer_lock:
            missed_data_count = 0
        reset_timer()
                
    except json.JSONDecodeError:
        logging.warning(f"Failed to decode JSON payload: {msg.payload}")
        print(f"Failed to decode JSON payload: {msg.payload}")
    except requests.exceptions.RequestException as e:
        logging.warning(f"Error while sending data to the API: {e}")
        print(f"Error while sending data to the API: {e}")
    except TemperatureOutOfRangeExeption as e:
        handle_temperature_exeptions(e, IMEI)
    except BatteryOutOfRangeException as e:
        handle_battery_exceptions(e, IMEI, battery)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, protocol=mqtt.MQTTv5)
        
def on_connect(client, userdata, flags, rc, properties = None):
    if rc == 0:
        print("Connected successfully.")
        client.subscribe(TOPIC)
        # Reset timer if connection was successfull
        reset_timer()
    else:
        print(f"Failed to connect with result code {rc}")
 


client.username_pw_set(USERNAME, PASSWORD)
client.on_connect = on_connect
client.on_message = on_message
 
try:
    client.connect(BROKER_HOST, BROKER_PORT, 60)
    client.loop_forever()
 
#If we reach this, we're screwed.
except Exception as e:
    logging.error(f"Failed to connect or run client: {e}")
    print(f"Failed to connect or run client: {e}")