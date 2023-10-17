# Sensor CSV to DB project
Processing sensor data in CSV format and insert them into database

## Project setup
### Install Docker
As the project rely on Docker, please install it first.

### Install DBeaver
For inspecting the database.

### Database Configuation
Open `.envs/.postgres` file, following settings can be seen:

```
POSTGRES_HOST=...
POSTGRES_PORT=...
POSTGRES_DB=...
POSTGRES_USER=...
POSTGRES_PASSWORD=...
```

`POSTGRES_HOST` means database address, please don't change that.

`POSTGRES_PORT` means database port, please don't change that.

`POSTGRES_DB` means database name, you may change it into different name.

`POSTGRES_USER` means database login username, you may change it into different username.

`POSTGRES_PASSWORD` means database login password, you may change it into different password.

Please note that you will need to delete docker volume `sensor_data_to_db_sensors_database_data
` after changing database name.

### Program Configuration
Open `config.json` file, following settings can be seen:

```
{
    "target_directory": ...,
    "number_of_process": ...
}
```

`target_directory` means directory that put all sensor CSV files, you may change it into different directory.

`number_of_process` means number of workers can be used when processing CSV files, you may change it to different number.

### Run Project
In Windows, open cmd and type
```
start_program.bat
```

In Ubuntu, open cmd and type
```
sudo ./start_program.sh
```

### Inspecting database
After the program execution finished, you may inspect the database in DBeaver by creating new connection.

Connection parameter can be found in **Database Configuation** section.
