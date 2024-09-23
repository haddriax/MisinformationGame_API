# database_orm
------------------------------------------------------
The backend is the fundamental component of the system, responsible for processing business logic, data access, and communication between the frontend and database. In our configuration, the backend comprises an app directory with subdirectories for API handling, database models, data generation, tests, and essential Python scripts for setup, cloud resource access, FastAPI application configuration, logging, and execution.

# Installation

## Python Virtual environment
First make a virtual environment in python. You might be ask to install virtual environments first.

```sh
python -m venv venv
```

## Windows
In windows you can activate the virtual environment by running the active script while you are in the `main` directory.

```sh
Venv\Scripts\activate
```

## Install packages
Install the packages with pip

```sh
pip install -r requirements.txt
```

## Configure settings

Configure the settings in the .env

- `Blob storage access`
- `MySQL database access`

## How to run 
Make sure you are in /app directory and run:

```sh
python main.py
```