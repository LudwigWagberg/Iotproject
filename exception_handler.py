from datetime import datetime, timedelta
from collections import deque
import logging
from send_email import send_email
from getlocation import get_location_by_imei
from logger_config import setup_logger

setup_logger()

# Initializes emty dictionarys to store timestamps of exceptions for each IMEI
temperature_exceptions_log_by_imei = {}
battery_exceptions_log_by_imei = {}
noData_exceptions_log = deque()

TEMPERATURE_EXCEPTION_THRESHOLD = 2 # 3 days
BATTERY_EXCEPTION_THRESHOLD = 1 # one week
NODATA_EXCEPTION_THRESHOLD = 1 # directly
TIME_WINDOW_HOURS = 168

def track_temperature_exception(IMEI, location):
    now = datetime.now()
    
    # checks if the IMEI alredy exists in the (temperature_exceptions_log_by_imei), if it does exsist it skips this code. 
    # If i dosent exist it creates a deque for that IMEI, which is used to store timestamps
    if IMEI not in temperature_exceptions_log_by_imei:
        temperature_exceptions_log_by_imei[IMEI] = deque()
    
    # Remove any entries older than 24 hours for the specific IMEI
    # Checks if the deque associated with the given IMEI has any elements, if the deque is emty this loop wont run.
    # If the deque is not emty it checks if the timestamp of the first enrty in the deque is older that TIME_WINDOW_HOURS (24 hours).
    # IF both of these contitions are true is removes the first enrty from the deque, until there are no entries older that 24 hours.
    # datetime - datetime = timedelta
    while temperature_exceptions_log_by_imei[IMEI] and (now - temperature_exceptions_log_by_imei[IMEI][0]) > timedelta(hours=TIME_WINDOW_HOURS):
        temperature_exceptions_log_by_imei[IMEI].popleft()
    
    # Add the current exception timestamp to the deque for the specific IMEI
    temperature_exceptions_log_by_imei[IMEI].append(now)
    
    # Checks if the length of the deque assosiated with that specific IMEI is longer that the threshold.
    # If its ture i send an email and then clears the stored deques for that IMEI.
    if len(temperature_exceptions_log_by_imei[IMEI]) > TEMPERATURE_EXCEPTION_THRESHOLD:
        # Send the email notification for the specific IMEI
        send_email(
                    "Alert: temperature reading out of range",
                    f"""\
                        An issue has been detected with one of the temperature measurements.
                        The reading is outside the acceptable range and requires your attention.
                        - Sensor ID: {IMEI}
                        - Location: {location}
                        Please investigate the cause of this anomaly and take appropriate action to resolve the issue.
                        """
                )
        temperature_exceptions_log_by_imei[IMEI].clear()


def track_battery_exception(IMEI, battery, location):
    now = datetime.now()
    
    if battery is not None:
        battery_percentage = (battery - 3.0) / (3.6 - 3.0) * 100
        battery_percentage = max(0, min(100, battery_percentage))  # Ensure the percentage stays within 0-100
    
    if IMEI not in battery_exceptions_log_by_imei:
        battery_exceptions_log_by_imei[IMEI] = deque()
    
    while battery_exceptions_log_by_imei[IMEI] and (now - battery_exceptions_log_by_imei[IMEI][0]) > timedelta(hours=TIME_WINDOW_HOURS):
        battery_exceptions_log_by_imei[IMEI].popleft()

    battery_exceptions_log_by_imei[IMEI].append(now)

    if len(battery_exceptions_log_by_imei[IMEI]) > BATTERY_EXCEPTION_THRESHOLD:

        send_email(
                    "Alert: The battery is running low",
                    f"""\
                    The battery of the following IoT is running low.
                    - Sensor ID: {IMEI}
                    - Location: {location}
 
                    The battery is at {battery_percentage:.2f}%.
                    Please take appropriate action to resolve the issue.
                    """
                )
        battery_exceptions_log_by_imei[IMEI].clear()


 
def track_noData_exception():
    now = datetime.now()
 
    # Remove any entries older than 24 hours
    while noData_exceptions_log and (now - noData_exceptions_log[0]) > timedelta(hours=TIME_WINDOW_HOURS):
        noData_exceptions_log.popleft()
 
    # Append the current exception timestamp
    noData_exceptions_log.append(now)
 
    # If the number of no-data exceptions exceeds the threshold, send an alert email
    if len(noData_exceptions_log) > NODATA_EXCEPTION_THRESHOLD:
 
        send_email(
            "Alert: No data received from IoT devices",
            """\
            An issue has been detected where the IoT devices have not sent any messages for the last 24 hours.
            The issue requires your attention.
            Please investigate the cause of this anomaly and take appropriate action to resolve it.
            """
        )
        # Clear the deque after sending the alert
        noData_exceptions_log.clear()
 
 

def handle_temperature_exeptions(e, IMEI):
    print(f"Handled Exception: {e} In IMEI: {IMEI}")
    logging.error(f"Handled Exception: {e} In IMEI: {IMEI}")
    
    location = get_location_by_imei(IMEI)
    
    track_temperature_exception(IMEI, location)

def handle_battery_exceptions(e, IMEI, battery):
    print(f"Handled Exception: {e} In IMEI: {IMEI}")
    logging.error(f"Handled Exception: {e}")

    location = get_location_by_imei(IMEI)
    
    track_battery_exception(IMEI, battery, location)
    
def handle_noData_exceptions(e):
    print(f"Handled Exception: {e}")
    logging.error(f"Handled Exception: {e}")
    
    track_noData_exception()
    