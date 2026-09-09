import psycopg
import os
from dotenv import load_dotenv

class DatabaseConnection:
    def __init__(self):
        load_dotenv()
        self.connection = psycopg.connect(
            host=os.environ['POSTGRES_HOST'],
            port=os.environ['POSTGRES_PORT'],
            dbname=os.environ['POSTGRES_DB'],
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD']
        )

    def get_connection(self):
        return self.connection

    def get_cursor(self):
        return self.connection.cursor()

    def close_connection(self):
        self.connection.close()