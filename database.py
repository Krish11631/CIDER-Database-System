import mysql.connector
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database="CIDER_HR" 
    )

def run_query(query):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        
        if query.strip().upper().startswith("SELECT"):
            result = cursor.fetchall()
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                df = pd.DataFrame(result, columns=columns)
            else:
                df = pd.DataFrame(result)
            conn.close()
            return df
        else:
            conn.commit()
            conn.close()
            return None
            
    except Exception as e:
        conn.close()
        raise e