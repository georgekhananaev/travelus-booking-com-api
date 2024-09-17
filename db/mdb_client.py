import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

load_dotenv()  # loading environment variables

environment = os.getenv('environment')

if environment == 'dev':
    connection_string = 'mongodb://george:george@localhost:27017/'
    print("This is the development environment.")
else:
    connection_string = f'mongodb+srv://{os.environ["MDB_USERNAME"]}:{os.environ["MDB_PASSWORD"]}@{os.environ["MDB_SERVER"]}/'  # noqa
    print("This is production environment.")

# clients
client = MongoClient(connection_string)  # setting mongodb client
client_motors = AsyncIOMotorClient(connection_string)  # setting async motors mongodb client

# synchronous
database = client['moonholidays']  # database name in mongodb
customers_db = client['customers']
finances_db = client['finances']
requests_db = client['requests']
messages_hub_db = client['messages_hub']

# asynchronous
moonholidays_motors = client_motors.moonholidays  # database name in mongodb
customers_motors = client_motors.customers
finances_motors = client_motors.finances
requests_motors = client_motors.requests
messages_hub_motors = client_motors.messages_hub