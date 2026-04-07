import os
from fastapi import FASTAPI 
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from mysql.connector import pooling 
from dotenv import load_dotenv

load_dotenv()
app = FASTAPI(title="Student Study Group Finder")
templates = Jinja2Templates(directionary="templates")

db_pool = pooling.MYSQLConnectionPool(
  pool_name = "studygroup_pool",
  host = os.getenv(""),
  user = os.getenv(""),
  pwd = os.getenv(""),
  database = os.getenv("")
)

def get_db_conn():
  return db_pool.get_connection()

def dashboard(request: Request):
  conn = get_db_conn
  cursor = conn.cursor(dictionary=True)
  try:
    cursor.execute()
  finally:
    cursor.close()
    conn.close()
   
