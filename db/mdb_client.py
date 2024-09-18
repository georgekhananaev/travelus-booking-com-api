import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

# Load environment variables from .env file
load_dotenv()

# Get the environment type (development or production)
environment = os.getenv('environment')

# Set the connection string based on the environment
if environment == 'development':
    # Connection string for the development environment
    connection_string = 'mongodb://george:george@localhost:27017/'
    print("This is the development environment.")
else:
    # Connection string for the production environment
    connection_string = f'mongodb+srv://{os.environ["MDB_USERNAME"]}:{os.environ["MDB_PASSWORD"]}@{os.environ["MDB_SERVER"]}/'
    print("This is the production environment.")

# MongoDB clients
client = MongoClient(connection_string)  # Synchronous MongoDB client
client_motors = AsyncIOMotorClient(connection_string)  # Asynchronous MongoDB client

# Define the booking database for async operations
booking_db = client_motors.booking  # The database name is 'booking'

# Test connection
if __name__ == '__main__':
    try:
        # Synchronous connection test
        print("Testing synchronous MongoDB connection...")
        print(client.server_info())  # This will print server information if connection is successful

        # Asynchronous connection test
        print("Testing asynchronous MongoDB connection...")


        async def test_async_connection():
            await booking_db.command("ping")  # Send a ping to check the async connection
            print("Asynchronous connection successful.")


        import asyncio

        asyncio.run(test_async_connection())  # Run the async test

    except Exception as e:
        print(f"Error occurred while connecting to MongoDB: {e}")
