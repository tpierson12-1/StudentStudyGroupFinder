import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv() #Reads .env -> os.envirson

#Now access securely:
def init_db():
  try:
    conn = mysql.connector.connect(
      host = os.getenv("DB_HOST"),
      user = os.getenv("DB_USER"),
      pwd = os.getenv("DB_Pass")
    )
    cursor = conn.cursor() 

    cursor.execute(f"CREATE DATABASE IF NOT EXIST {os.getenv('DB_NAME')}")
    cursor.execute(f"USE {os.getenv('DB_NAME')}")
    
    tables = {

    }
    
  except Exception as e:
    print(f"CRITICAL ERROR during DB Setup: {e}")
    
  finally:
    if __name__ == "__main__":
      init_db()
