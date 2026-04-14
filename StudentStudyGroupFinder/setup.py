import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv() #Reads .env -> os.envirson

#Now access securely:
def init_db():
  try:
    conn = mysql.connector.connect(
      host = os.getenv("localhost"),
      user = os.getenv("root"),
      pwd = os.getenv("DB_Pass") # You can put whatever password in there
    )
    cursor = conn.cursor() 

    cursor.execute(f"CREATE DATABASE IF NOT EXIST {os.getenv('GroupFinderDB')}")
    cursor.execute(f"USE {os.getenv('GroupFinderDB')}")
    
    tables = {
      "APP_USER": "CREATE TABLE IF NOT EXISTS APP_USER (User_ID INT AUTO_INCREMENT PRIMARY KEY,  User_Email VARCHAR(255) NOT NULL UNIQUE, User_PasswordHash VARCHAR(255) NOT NULL, User_DisplayName VARCHAR(100) UNIQUE, User_Bio TEXT, User_CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP, User_AccountStatus VARCHAR(20)",
     
      "Tutor": "CREATE TABLE IF NOT EXISTS Tutor (User_ID INT PRIMARY KEY, Tutor_Expertise VARCHAR(255), Tutor_Availability VARCHAR(255), FOREIGN KEY (User_ID) REFERENCES APP_USER(User_ID)",
     
      "STUDY_GROUP": "CREATE TABLE IF NOT EXISTS STUDY_GROUP(Group_ID INT AUTO_INCREMENT PRIMARY KEY, Group_Title VARCHAR(100) NOT NULL, Group_Description TEXT, Group_PrivacyLevel VARCHAR(20), Group_SkillLevel VARCHAR(20), Group_CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP, Owner_User_ID INT NOT NULL, FOREIGN KEY (Owner_User_ID) REFERENCES APP_USER(User_ID)",
     
      "GroupMembership": "CREATE TABLE IF NOT EXISTS GroupMembership(Group_ID INT NOT NULL, User_ID INT NOT NULL, GroupMembership_Role VARCHAR(35), GroupMembership_JoinStatus VARCHAR(20), GroupMembership_JoinedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (Group_ID, User_ID), FOREIGN KEY (Group_ID) REFERENCES STUDY_GROUP(Group_ID), FOREIGN KEY (User_ID) REFERENCES APP_USER(User_ID)",
     
      "Topic": "CREATE TABLE IF NOT EXISTS Topic(Topic_ID INT AUTO_INCREMENT PRIMARY KEY, Topic_Name VARCHAR(100) NOT NULL, Topic_Category VARCHAR(100)",
     
      "GroupTopic": "CREATE TABLE IF NOT EXISTS GroupTopic(Group_ID INT NOT NULL, Topic_ID INT NOT NULL, PRIMARY KEY (Group_ID, Topic_ID), FOREIGN KEY (Group_ID) REFERENCES STUDY_GROUP(Group_ID), FOREIGN KEY (Topic_ID) REFERENCES Topic(Topic_ID)",
     
      "Location": "CREATE TABLE IF NOT EXISTS Location(Location_ID INT AUTO_INCREMENT PRIMARY KEY,  Location_Type VARCHAR(20), Location_MeetingLink VARCHAR(255), Location_AddressLine1 VARCHAR(255), Location_City VARCHAR(80), Location_State VARCHAR(30), Location_Zip VARCHAR(5)",
     
      "Session": "CREATE TABLE IF NOT EXISTS Session( Session_ID INT AUTO_INCREMENT PRIMARY KEY, Group_ID INT NOT NULL, Host_User_ID INT, Location_ID INT, Session_StartDateTime TIMESTAMP, Session_EndDateTime TIMESTAMP, Session_Capacity INT, Session_Notes TEXT, FOREIGN KEY (Group_ID) REFERENCES STUDY_GROUP(Group_ID), FOREIGN KEY (Host_User_ID) REFERENCES APP_USER(User_ID), FOREIGN KEY (Location_ID) REFERENCES Location(Location_ID)",
     
      "SessionRSVP": "CREATE TABLE IF NOT EXISTS SessionRSVP(Session_ID INT NOT NULL, User_ID INT NOT NULL, SessionRSVP_Status VARCHAR(20), SessionRSVP_Time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (Session_ID, User_ID), FOREIGN KEY (User_ID) REFERENCES APP_USER(User_ID),  FOREIGN KEY (Session_ID) REFERENCES Session(Session_ID)"
    }
    
    for name, ddl in tables.items():
      cursor.execute(ddl)
      print(f"Table '{name}' verified.")

    cursor.execute("INSERT INTO APP_USER VALUES((1, 'alex@example.com', 'hash1', 'alex23', 'Computer science student looking for study partners.', 'Active'), (2, 'brianna@example.com', 'hash2', 'briannaK', 'Enjoys group study for math and programming.', 'Active'), (3, 'carlos@example.com', 'hash3', 'carlos_dev', 'Prefers evening study sessions.', 'Active'), (4, 'dana@example.com', 'hash4', 'dana_sci', 'Interested in tutoring database concepts.', 'Active'), (5, 'ethan@example.com', 'hash5', 'ethanM', 'Needs help with calculus and physics.', 'Active')")
    cursor.execute("INSERT INTO Tutor VALUES (User_ID, Tutor_Expertise, Tutor_Availability) (2, 'Calculus, Algebra', 'Mon/Wed 5PM-8PM'), (4, 'Databases, SQL, Python', 'Tue/Thu 4PM-7PM')")
    cursor.execute("INSERT INTO Topic VALUES (1, 'SQL', 'Computer Science'), (2, 'Database Design', 'Computer Science'), (3, 'Calculus I', 'Mathematics'), (4, 'Physics I', 'Science'), (5, 'Python Programming', 'Computer Science'))")
    cursor.execute("INSERT INTO STUDY_GROUP VALUES (1, 'Database Systems Study Group', 'Study group for database design, SQL, and course review.', 'Public', 'Intermediate', 1), (2, 'Calculus Review Group', 'Weekly review for derivatives, limits, and practice problems.', 'Public', 'Beginner', 2), (3, 'Python Project Team', 'Collaborative coding and debugging practice.', 'Private', 'Intermediate', 4))")
    cursor.execute("INSERT INTO GroupMembership VALUES (1, 1, 'Owner', 'Joined'), (1, 3, 'Member', 'Joined'), (1, 4, 'Tutor', 'Joined'), (2, 2, 'Owner', 'Joined'), (2, 5, 'Member', 'Joined'), (3, 4, 'Owner', 'Joined'), (3, 1, 'Member', 'Joined'), (3, 3, 'Member', 'Pending'))")
    cursor.execute("INSERT INTO GroupTopic VALUES (1, 1), (1, 2), (2, 3), (3, 5))")
    cursor.execute("INSERT INTO Location VALUES (1, 'Online', 'https://zoom.us/j/123456789', NULL, NULL, NULL, NULL), (2, 'InPerson', NULL, '318 Meadow Brook Rd', 'Rochester', 'MI', '48309'), (3, 'Online', 'https://meet.google.com/abc-defg-hij', NULL, NULL, NULL, NULL))")
    cursor.execute("INSERT INTO Session VALUES (1, 1, 4, 1, '2026-04-15 18:00:00', '2026-04-15 19:30:00', 15, 'Review SQL joins and normalization.'), (2, 2, 2, 2, '2026-04-16 17:00:00', '2026-04-16 18:30:00', 20, 'Calculus exam prep session.'), (3, 3, 4, 3, '2026-04-17 19:00:00', '2026-04-17 20:30:00', 10, 'Work on Python project tasks.');)")
    cursor.execute("INSERT INTO Session RSVP VALUES (1, 1, 'Going'), (1, 3, 'Going'), (1, 4, 'Going'), (2, 2, 'Going'), (2, 5, 'Interested'), (3, 1, 'Going'), (3, 3, 'Pending'), (3, 4, 'Going');)")

    conn.commit()
    print("---Database Setup Finished----")
 
  except Exception as e:
    print(f"DB Error: {e}")
    
  finally:
    if 'conn' in locals() and conn.is_connected():
      cursor.close()
      conn.close()
if __name__ == '__main__':
  init_db()
