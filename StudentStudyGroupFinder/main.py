import os
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import mysql.connector
from dotenv import load_dotenv
import bcrypt

load_dotenv()

app = FastAPI(title="Student Study Group Finder")
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "changeme-secret-key"))
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False


def get_db_conn():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASS", ""),
        database=os.getenv("DB_NAME", "GroupFinderDB")
    )


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse(request, "login.html", {"error": None})


@app.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...)):
    error = None
    try:
        conn = get_db_conn()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM APP_USER WHERE User_Email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user and verify_password(password, user["User_PasswordHash"]):
            request.session["user_id"] = user["User_ID"]
            request.session["username"] = user["User_DisplayName"]
            return RedirectResponse(url="/dashboard", status_code=303)
        else:
            error = "Invalid email or password."
    except Exception as e:
        error = f"Database error: {e}"
    return templates.TemplateResponse(request, "login.html", {"error": error})


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse(request, "register.html", {"error": None})


@app.post("/register")
def register(
    request: Request,
    fname: str = Form(...),
    lname: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_pwd: str = Form(...),
):
    error = None
    if password != confirm_pwd:
        error = "Passwords do not match."
    elif len(password) < 8:
        error = "Password must be at least 8 characters."
    else:
        try:
            conn = get_db_conn()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT User_ID FROM APP_USER WHERE User_Email = %s", (email,))
            if cursor.fetchone():
                error = "An account with that email already exists."
            else:
                hashed = hash_password(password)
                display_name = f"{fname} {lname}"
                cursor.execute(
                    "INSERT INTO APP_USER (User_Email, User_PasswordHash, User_DisplayName, User_AccountStatus) VALUES (%s, %s, %s, 'Active')",
                    (email, hashed, display_name),
                )
                conn.commit()
                cursor.close()
                conn.close()
                return RedirectResponse(url="/login", status_code=303)
            cursor.close()
            conn.close()
        except Exception as e:
            error = f"Database error: {e}"
    return templates.TemplateResponse(request, "register.html", {"error": error})


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)
    try:
        conn = get_db_conn()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT STUDY_GROUP.Group_Title, GroupMembership.GroupMembership_Role
               FROM GroupMembership
               JOIN STUDY_GROUP ON GroupMembership.Group_ID = STUDY_GROUP.Group_ID
               WHERE GroupMembership.User_ID = %s""",
            (user_id,),
        )
        my_groups = cursor.fetchall()
        cursor.execute("SELECT * FROM STUDY_GROUP")
        all_groups = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception:
        my_groups = []
        all_groups = []
    return templates.TemplateResponse(request, "dashboard.html", {
        "my_groups": my_groups,
        "all_groups": all_groups,
        "username": request.session.get("username"),
    })


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)
