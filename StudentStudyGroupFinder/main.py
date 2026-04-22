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
    is_tutor: str = Form(""),
    expertise: str = Form(""),
    availability: str = Form(""),
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
                user_id = cursor.lastrowid
                if is_tutor == "yes":
                    cursor.execute(
                        "INSERT INTO Tutor (User_ID, Tutor_Expertise, Tutor_Availability) VALUES (%s, %s, %s)",
                        (user_id, expertise, availability),
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
            """SELECT STUDY_GROUP.Group_ID, STUDY_GROUP.Group_Title, GroupMembership.GroupMembership_Role
               FROM GroupMembership
               JOIN STUDY_GROUP ON GroupMembership.Group_ID = STUDY_GROUP.Group_ID
               WHERE GroupMembership.User_ID = %s AND GroupMembership.GroupMembership_JoinStatus = TRUE""",
            (user_id,),
        )
        my_groups = cursor.fetchall()
        my_group_ids = {g["Group_ID"] for g in my_groups}
        cursor.execute("SELECT Group_ID, Group_Title, Group_Description, Group_PrivacyLevel, Group_SkillLevel FROM STUDY_GROUP")
        all_groups = cursor.fetchall()
        available_groups = [g for g in all_groups if g["Group_ID"] not in my_group_ids]
        cursor.close()
        conn.close()
    except Exception:
        my_groups = []
        available_groups = []
    return templates.TemplateResponse(request, "dashboard.html", {
        "my_groups": my_groups,
        "available_groups": available_groups,
        "username": request.session.get("username"),
    })


@app.get("/creategroup", response_class=HTMLResponse)
def creategroup_page(request: Request):
    if not request.session.get("user_id"):
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse(request, "creategroup.html", {"error": None})


@app.post("/creategroup")
def creategroup(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    privacy: str = Form("Public"),
    skill_level: str = Form("Beginner"),
):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO STUDY_GROUP (Group_Title, Group_Description, Group_PrivacyLevel, Group_SkillLevel, Owner_User_ID) VALUES (%s, %s, %s, %s, %s)",
            (title, description, privacy, skill_level, user_id),
        )
        group_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO GroupMembership (Group_ID, User_ID, GroupMembership_Role, GroupMembership_JoinStatus) VALUES (%s, %s, 'Owner', TRUE)",
            (group_id, user_id),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return RedirectResponse(url="/dashboard", status_code=303)
    except Exception as e:
        return templates.TemplateResponse(request, "creategroup.html", {"error": f"Database error: {e}"})


@app.post("/joingroup")
def joingroup(request: Request, group_id: int = Form(...)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO GroupMembership (Group_ID, User_ID, GroupMembership_Role, GroupMembership_JoinStatus)
               VALUES (%s, %s, 'Member', TRUE)
               ON DUPLICATE KEY UPDATE GroupMembership_JoinStatus = TRUE""",
            (group_id, user_id),
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception:
        pass
    return RedirectResponse(url="/dashboard", status_code=303)


@app.post("/leavegroup")
def leavegroup(request: Request, group_id: int = Form(...)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE GroupMembership SET GroupMembership_JoinStatus = FALSE WHERE User_ID = %s AND Group_ID = %s",
            (user_id, group_id),
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception:
        pass
    return RedirectResponse(url="/dashboard", status_code=303)


@app.get("/group/{group_id}", response_class=HTMLResponse)
def group_detail(request: Request, group_id: int):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)
    try:
        conn = get_db_conn()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """SELECT STUDY_GROUP.*, APP_USER.User_DisplayName AS Owner_Name
               FROM STUDY_GROUP
               JOIN APP_USER ON STUDY_GROUP.Owner_User_ID = APP_USER.User_ID
               WHERE STUDY_GROUP.Group_ID = %s""",
            (group_id,),
        )
        group = cursor.fetchone()

        cursor.execute(
            """SELECT APP_USER.User_DisplayName, GroupMembership.GroupMembership_Role, GroupMembership.GroupMembership_JoinedAt
               FROM GroupMembership
               JOIN APP_USER ON GroupMembership.User_ID = APP_USER.User_ID
               WHERE GroupMembership.Group_ID = %s AND GroupMembership.GroupMembership_JoinStatus = TRUE""",
            (group_id,),
        )
        members = cursor.fetchall()

        cursor.execute(
            """SELECT Session.*, Location.Location_Type, Location.Location_MeetingLink,
                      Location.Location_AddressLine1, Location.Location_City,
                      Location.Location_State, Location.Location_Zip
               FROM Session
               LEFT JOIN Location ON Session.Location_ID = Location.Location_ID
               WHERE Session.Group_ID = %s
               ORDER BY Session.Session_StartDateTime""",
            (group_id,),
        )
        sessions = cursor.fetchall()

        for session in sessions:
            cursor.execute(
                """SELECT APP_USER.User_DisplayName, SessionRSVP.SessionRSVP_Status
                   FROM SessionRSVP
                   JOIN APP_USER ON SessionRSVP.User_ID = APP_USER.User_ID
                   WHERE SessionRSVP.Session_ID = %s""",
                (session["Session_ID"],),
            )
            session["rsvps"] = cursor.fetchall()

        cursor.execute(
            """SELECT Topic.Topic_Name, Topic.Topic_Category
               FROM GroupTopic
               JOIN Topic ON GroupTopic.Topic_ID = Topic.Topic_ID
               WHERE GroupTopic.Group_ID = %s""",
            (group_id,),
        )
        topics = cursor.fetchall()

        cursor.execute(
            """SELECT GroupMembership_Role FROM GroupMembership
               WHERE Group_ID = %s AND User_ID = %s AND GroupMembership_JoinStatus = TRUE""",
            (group_id, user_id),
        )
        membership = cursor.fetchone()

        cursor.close()
        conn.close()
    except Exception as e:
        return templates.TemplateResponse(request, "group.html", {"error": str(e), "group": None})

    return templates.TemplateResponse(request, "group.html", {
        "group": group,
        "members": members,
        "sessions": sessions,
        "topics": topics,
        "user_id": user_id,
        "membership": membership,
    })


@app.get("/createsession/{group_id}", response_class=HTMLResponse)
def createsession_page(request: Request, group_id: int):
    if not request.session.get("user_id"):
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse(request, "createsession.html", {"group_id": group_id, "error": None})


@app.post("/createsession")
def createsession(
    request: Request,
    group_id: int = Form(...),
    start: str = Form(...),
    end: str = Form(...),
    capacity: int = Form(...),
    notes: str = Form(""),
    location_type: str = Form(...),
    meeting_link: str = Form(""),
    address: str = Form(""),
    city: str = Form(""),
    state: str = Form(""),
    zip_code: str = Form(""),
):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        if location_type == "Online":
            cursor.execute(
                "INSERT INTO Location (Location_Type, Location_MeetingLink) VALUES ('Online', %s)",
                (meeting_link,),
            )
        else:
            cursor.execute(
                "INSERT INTO Location (Location_Type, Location_AddressLine1, Location_City, Location_State, Location_Zip) VALUES ('In-Person', %s, %s, %s, %s)",
                (address, city, state, zip_code),
            )
        location_id = cursor.lastrowid
        cursor.execute(
            """INSERT INTO Session (Group_ID, Host_User_ID, Location_ID, Session_StartDateTime, Session_EndDateTime, Session_Capacity, Session_Notes)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (group_id, user_id, location_id, start, end, capacity, notes),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return RedirectResponse(url=f"/group/{group_id}", status_code=303)
    except Exception as e:
        return templates.TemplateResponse(request, "createsession.html", {"group_id": group_id, "error": f"Database error: {e}"})


@app.post("/deletegroup")
def deletegroup(request: Request, group_id: int = Form(...)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)
    try:
        conn = get_db_conn()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT Owner_User_ID FROM STUDY_GROUP WHERE Group_ID = %s", (group_id,)
        )
        group = cursor.fetchone()
        if not group or group["Owner_User_ID"] != user_id:
            cursor.close()
            conn.close()
            return RedirectResponse(url="/dashboard", status_code=303)
        cursor.execute("DELETE FROM SessionRSVP WHERE Session_ID IN (SELECT Session_ID FROM Session WHERE Group_ID = %s)", (group_id,))
        cursor.execute("DELETE FROM Session WHERE Group_ID = %s", (group_id,))
        cursor.execute("DELETE FROM GroupMembership WHERE Group_ID = %s", (group_id,))
        cursor.execute("DELETE FROM GroupTopic WHERE Group_ID = %s", (group_id,))
        cursor.execute("DELETE FROM STUDY_GROUP WHERE Group_ID = %s", (group_id,))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception:
        pass
    return RedirectResponse(url="/dashboard", status_code=303)


@app.get("/tutors", response_class=HTMLResponse)
def tutors(request: Request):
    if not request.session.get("user_id"):
        return RedirectResponse(url="/login", status_code=302)
    try:
        conn = get_db_conn()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT APP_USER.User_DisplayName, Tutor.Tutor_Expertise, Tutor.Tutor_Availability
               FROM Tutor
               JOIN APP_USER ON Tutor.User_ID = APP_USER.User_ID"""
        )
        tutor_list = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception:
        tutor_list = []
    return templates.TemplateResponse(request, "tutors.html", {"tutors": tutor_list})


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)
