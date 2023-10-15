from concurrent.futures import ProcessPoolExecutor as parallel_tasks_pool
from csv import reader as csv_reader
from datetime import datetime as DateTime
from json import load as load_json_file
from os import getenv as os_getenv
from os import listdir as os_list_dir
from os import path as os_path

from dotenv import load_dotenv
from psycopg2 import connect as connect_postgres_db
from psycopg2.errors import UniqueViolation as PostGresDB_UniqueViolation

load_dotenv(os_path.join(".envs", ".postgres"))

POSTGRES_HOST = os_getenv('POSTGRES_HOST')
POSTGRES_PORT = os_getenv('POSTGRES_PORT')
POSTGRES_DB = os_getenv('POSTGRES_DB')
POSTGRES_USER = os_getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os_getenv('POSTGRES_PASSWORD')

with open("config.json") as json_file:
    # Load its content and make a new dictionary
    data = load_json_file(json_file)
    CSV_DIRECTORY = data["target_directory"]
    NUMBER_OF_PROCESS = data["number_of_process"]


def create_tables():
    # create DB connection
    conn = connect_postgres_db(
        database=POSTGRES_DB,
        host=POSTGRES_HOST,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        port=POSTGRES_PORT
    )

    cursor = conn.cursor()

    create_sensors_table_sql = '''
        CREATE TABLE IF NOT EXISTS Sensors (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL,

            CONSTRAINT name_unique
                UNIQUE (name)
        );
    '''

    create_readings_table_sql = '''
        CREATE TABLE IF NOT EXISTS Readings (
            id SERIAL PRIMARY KEY,
            datetime TIMESTAMPTZ NOT NULL,
            sensor_id INT NOT NULL,
            value INTEGER NOT NULL,

            CONSTRAINT fk_sensor_id
                FOREIGN KEY(sensor_id)
                    REFERENCES Sensors(id),

            CONSTRAINT record_unique
                UNIQUE (datetime, sensor_id, value)
        );
    '''

    cursor.execute(create_sensors_table_sql)
    cursor.execute(create_readings_table_sql)
    cursor.close()

    # commit the changes
    conn.commit()
    conn.close()

    return None


def check_vaild_data(datetime_string, value_string):
    try:
        return (
            DateTime.fromisoformat(datetime_string),
            int(value_string)
        )
    except ValueError:
        return (False, False)


def csv_to_db(filename):
    # create DB connection
    conn = connect_postgres_db(
        database=POSTGRES_DB,
        host=POSTGRES_HOST,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        port=POSTGRES_PORT
    )

    cursor = conn.cursor()
    datetime = None
    sensor_id = 0
    value = 0

    with open(filename, "r") as csv_file:
        print(f"Processing {filename}...")
        data_reader = csv_reader(csv_file, delimiter=",")
        next(data_reader, None)
        for row in data_reader:
            # insert sensor into Sensors table
            try:
                cursor.execute(
                    '''
                    INSERT INTO Sensors(name)
                    VALUES(%s)
                    RETURNING id;
                    ''',
                    (row[1],)
                )

                result = cursor.fetchone()

                if result:
                    sensor_id = result[0]

                conn.commit()

            except PostGresDB_UniqueViolation:
                conn.rollback()

                cursor.execute(
                    '''
                    SELECT id
                    FROM Sensors
                    WHERE name = %s;
                    ''',
                    (row[1],)
                )

                result = cursor.fetchone()

                if result:
                    sensor_id = result[0]

                conn.commit()

            # insert readings into Readings table
            datetime, value = check_vaild_data(row[0], row[-1])

            if datetime and value:
                try:
                    cursor.execute(
                        '''
                        INSERT INTO Readings(datetime, sensor_id, value)
                        VALUES(%s, %s, %s);
                        ''',
                        (datetime, sensor_id, value)
                    )

                    conn.commit()

                except PostGresDB_UniqueViolation:
                    conn.rollback()
                    print(f"> Skipping duplicated row: {row}...")

            else:
                print(f"> Skipping row with invaild data: {row}...")

    cursor.close()
    conn.close()

    return None


def main():
    # csv_directory = "sensor_data"

    task_pool = parallel_tasks_pool(max_workers=10)
    task_futures = []

    create_tables()

    for csv_filename in os_list_dir(CSV_DIRECTORY):
        task_futures.append(
            task_pool.submit(
                csv_to_db,
                os_path.join(CSV_DIRECTORY, csv_filename)
            )
        )

    for task_future in task_futures:
        task_future.result()

    print("> Shutting down task pool...")
    task_pool.shutdown()

    print("> All CSV file are inserted into database.")
    return 0


if __name__ == '__main__':
    main()
