import mysql.connector
import os
from dotenv import load_dotenv
import pandas as pd

# Load the passwords from the .env file
load_dotenv()

def get_connection():
    """Establishes a connection to the MySQL server."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def run_query(query):
    """A helper function to run a query and return a Pandas DataFrame."""
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df