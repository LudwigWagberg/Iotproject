from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Dict
import mariadb
import sys
import os
import logging
import json
import os
from datetime import datetime
from logger_config import setup_logger

setup_logger()

# Create a FastAPI instance
app = FastAPI()

class Timestamps(BaseModel):
    temperature1: float
    temperature2: float
    temperature3: float
    timestamp: str

class temperatureData(BaseModel):
    IMEI: int = Field(..., example="123456789012345")
    Model: str = Field(..., example="DeviceModel123")
    temperature1: float = Field(..., example=25.0)
    temperature2: float = Field(..., example=26.0)
    temperature3: float = Field(..., example=24.5)
    battery: float = Field(..., example=80.0)
    signal: int = Field(..., example=100)
    timestamps: Dict[str, Timestamps]

database_password = os.getenv('DATABASE_PASSWORD')

# Database connection setup
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

def format_date(date_str: str) -> str:
    # Convert from 'YYYY/MM/DD HH:MM:SS' to 'YYYY-MM-DD HH:MM:SS'
    try:
        dt = datetime.strptime(date_str, '%Y/%m/%d %H:%M:%S')
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        print(f"Date format error: {date_str}")
        logging.error(f"Data formatt error: {date_str}")
        return None

def insert_into_db(IMEI: str, date: str, temperature: float, battery: float, signal: int):
    try:
        # Use backticks to escape column IMEIs that contain special characters
        insert_query = """
        INSERT INTO sensor_data (`IMEI`, `date`, `temperature`, `battery`, `signal`)
        VALUES (%s, %s, %s, %s, %s)
        """
        # Execute the SQL query
        cur.execute(insert_query, (IMEI, date, temperature, battery, signal))
        conn.commit()
        print("Data inserted successfully into sensor_data")
    except mariadb.Error as e:
        print(f"Error inserting data into MariaDB: {e}")
        logging.error(f"Error inserting data into MariaDB: {e}")
        
@app.post("/temperature")
async def receive_temperature(data: temperatureData):
    try:
        # Log the incoming data
        data_dict = data.model_dump()
        pretty_print = json.dumps(data_dict, indent = 4)
        
        print(f"Received data: {pretty_print}")

        # Log specific fields
        print(f"Device IMEI: {data.IMEI}, Model: {data.Model}")
        print(f"temperature 1: {data.temperature1}, Battery: {data.battery}, Signal: {data.signal}")

        # Loop through each timestamp and insert the data
        for _, timestamp_data in data.timestamps.items():
            # Prepare data for insertion
            IMEI = data.IMEI
            date = format_date(timestamp_data.timestamp)
            temperature = timestamp_data.temperature1
            battery = data.battery
            signal = data.signal

            # Check if date formatting was successful
            if date is not None:
                # Insert into the database
                insert_into_db(IMEI, date, temperature, battery, signal)
            else:
                print(f"Invalid date format for timestamp {timestamp_data.timestamp}")
                logging.error(f"Invalid date format for timestamp {timestamp_data.timestamp}")
                                
        # Return a success response with the status code 200
        return {"message": "temperature data received and stored successfully"}

    except Exception as e:
        print(f"Error while processing temperature data: {e}")
        logging.error(f"Error while processing temperature data: {e}")

        raise HTTPException(status_code=500, detail="Internal server error")

@app.exception_handler(422)
async def validation_exception_handler(request: Request, exc):
    # Log the error details
    print(f"Validation error for request {request}: {exc}")
    logging.error(f"Validation error for request {request}: {exc}")
    return {"message": "Validation error", "details": exc.errors()}