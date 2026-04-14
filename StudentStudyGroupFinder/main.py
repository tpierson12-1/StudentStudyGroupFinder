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
  host = os.getenv("localhost"),
  user = os.getenv("root"),
  pwd = os.getenv(""), # You can put what password in there
  database = os.getenv("GroupFinderDB")
)

def get_db_conn():
  return db_pool.get_connection()

@app.get("/")
def dashboard(request: Request):
  conn = get_db_conn
  cursor = conn.cursor(dictionary=True)
  try:
    cursor.execute("SELECT * FROM STUDY_GROUP")
    STUDY_GROUP = cursor.fetchall()
    query = "\SELECT  GroupMembership.User_ID, GroupMembership.GroupMembership_Role, STUDY_GROUP.Group_Title FROM GroupMembership JOIN STUDY_GROUP ON GroupMembership.Group_ID = STUDY_GROUP.Group_ID WHERE GroupMembership.User_ID = %s;"
    cursor.execute(query)
    v_GroupList = cursor.fetchall()

    return templates.TemplateResponse(
      request = request,
      name = "dashboard.html",
      context = {"GroupTopic": GroupTopic, "v_GroupList": v_GroupList}
    )
  finally:
    cursor.close()
    conn.close()

@app.post("/studygroup")
def studygroup():
  conn = get_db_conn()
  cursor = conn.cursor()
  try:
    cursor.execute("")
    cursor.execute("")
    conn.comit()
  except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
  finally:
    cursor.close()
    conn.close()
  return RedirectResponse(url="/", status_code = 303)

    

     
   
  


    

