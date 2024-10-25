import mariadb
import logging
import os
import sys
import os

# Database connection setup
database_password = os.getenv('DATABASE_PASSWORD')

try:
    conn = mariadb.connect(
        user="root",
        password=database_password,
        host="localhost",
        port=3306, 
        database="iot_data"
    )
    print("Successfully connected to the MariaDB Platform.")
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    logging.error(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

cur = conn.cursor()

def get_location_by_imei(IMEI):
    try:
        query = 'SELECT location FROM sensor_info WHERE IMEI = ?'
        cur.execute(query, (IMEI,))
        result = cur.fetchone()
        print(f"Fetching location for IMEI: {IMEI}")
        if result:
            return result[0]
        else:
            return "Unknown location"
    except mariadb.Error as e:
        print(f"Error fetching location for IMEI {IMEI}: {e}")
        logging.error(f"Error fetching location for IMEI {IMEI}: {e}")
        return "Database Error"
