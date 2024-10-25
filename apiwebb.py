from fastapi import FastAPI
import sys
import mariadb
import os
from custom_exeption import DatabaseConnectionError, SensorDataNotFound

app = FastAPI()

database_password = os.getenv('DATABASE_PASSWORD')

def get_db_connection():
    try:
        conn = mariadb.connect(
            user="root",
            password=database_password,
            host="localhost",
            port=3306,
            database="iot_data",
        )

        print("Successfully connected to the MariaDB Platform.")
        return conn
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        raise DatabaseConnectionError(f"Error connection to MariaDB: {e}")


@app.get("/livetemp/{location}")
async def read_sensor_data(location: str):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT sd.`imei`, sd.`date`, sd.`temperature`, 
                    si.`location`
                    FROM `sensor_data` sd
                    JOIN `sensor_info` si ON sd.`imei` = si.`imei`
                    WHERE si.`location` = %s
                    ORDER BY sd.`date` DESC
                    LIMIT 1;""",
                    (location,),
                )
                result = cur.fetchone()

        if result:
            return {
                "IMEI": result[0],
                "date": result[1],
                "temperature": result[2],
                "location": result[3],
            }
        else:
            raise SensorDataNotFound("Sensor data not found")

    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        raise DatabaseConnectionError(
            f"In endpoint 'livetemp':Error connection to MariaDB: {e}"
        )


@app.get("/previousfive/{location}")
async def read_sensor_data_previous_five(location: str):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """ 
                SELECT DATE_FORMAT(sd.`date`, '%m-%d') AS `day`, 
                sd.`temperature` AS `avg_temperature` 
                FROM `sensor_data` sd
		        JOIN `sensor_info` si ON sd.`imei` = si.`imei`
		        WHERE si.`location` = %s
                AND sd.`date` >= CURDATE() - INTERVAL 5 DAY AND sd.`date` < CURDATE()  
                GROUP BY `day`
		        ORDER BY `day` DESC;
		        """,
                    (location,),
                )

                results = cur.fetchall()

        if results:
            return [
                {"location": location, "date": row[0], "average_temperature": row[1]}
                for row in results
            ]
        else:
            raise SensorDataNotFound("Sensor data not found")

    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        raise DatabaseConnectionError(
            f"In endpoint 'previousfive': Error connection to MariaDB: {e}"
        )


@app.get("/info")
async def read_sensor_info():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM `sensor_info`;")
                results = cur.fetchall()

            if results:
                return [
                    {
                        "IMEI": row[0],
                        "Location": row[1],
                        "Lattitude": row[2],
                        "Longitude": row[3],
                    }
                    for row in results
                ]
            else:
                raise SensorDataNotFound("Sensor data not found")

    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        raise DatabaseConnectionError(
            f"In endpoint 'info': Error connection to MariaDB: {e}"
        )