DROP DATABASE IF EXISTS GroupFinderDB;
CREATE DATABASE GroupFinderDB;
USE GroupFinderDB;

CREATE TABLE APP_USER (
    User_ID INT AUTO_INCREMENT PRIMARY KEY,
    User_Email VARCHAR(255) NOT NULL UNIQUE,
    User_PasswordHash VARCHAR(255) NOT NULL,
    User_DisplayName VARCHAR(100) UNIQUE,
    User_Bio TEXT,
    User_CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    User_AccountStatus VARCHAR(20) DEFAULT 'Active'
);

CREATE TABLE UserStatusHistory (
    StatusHistory_ID INT AUTO_INCREMENT PRIMARY KEY,
    User_ID INT NOT NULL,
    Old_Status VARCHAR(20),
    New_Status VARCHAR(20) NOT NULL,
    ChangedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ChangedBy_User_ID INT,

    FOREIGN KEY (User_ID) REFERENCES APP_USER(User_ID) ON DELETE CASCADE,
    FOREIGN KEY (ChangedBy_User_ID) REFERENCES APP_USER(User_ID) ON DELETE SET NULL
);

CREATE TABLE Tutor (
    User_ID INT PRIMARY KEY,
    Tutor_Expertise VARCHAR(255),
    Tutor_Availability VARCHAR(255),

    FOREIGN KEY (User_ID) REFERENCES APP_USER(User_ID) ON DELETE CASCADE
);

CREATE TABLE STUDY_GROUP (
    Group_ID INT AUTO_INCREMENT PRIMARY KEY,
    Group_Title VARCHAR(100) NOT NULL,
    Group_Description TEXT,
    Group_PrivacyLevel VARCHAR(20),
    Group_SkillLevel VARCHAR(20),
    Group_CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Owner_User_ID INT NOT NULL,

    FOREIGN KEY (Owner_User_ID) REFERENCES APP_USER(User_ID)
);

CREATE TABLE GroupMembership (
    Group_ID INT NOT NULL,
    User_ID INT NOT NULL,
    GroupMembership_Role VARCHAR(35) DEFAULT 'Member',
    GroupMembership_JoinStatus BOOLEAN DEFAULT TRUE,
    GroupMembership_JoinedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (Group_ID, User_ID),
    FOREIGN KEY (Group_ID) REFERENCES STUDY_GROUP(Group_ID) ON DELETE CASCADE,
    FOREIGN KEY (User_ID) REFERENCES APP_USER(User_ID) ON DELETE CASCADE
);

CREATE TABLE Topic (
    Topic_ID INT AUTO_INCREMENT PRIMARY KEY,
    Topic_Name VARCHAR(100) NOT NULL,
    Topic_Category VARCHAR(100)
);

CREATE TABLE GroupTopic (
    Group_ID INT NOT NULL,
    Topic_ID INT NOT NULL,

    PRIMARY KEY (Group_ID, Topic_ID),
    FOREIGN KEY (Group_ID) REFERENCES STUDY_GROUP(Group_ID) ON DELETE CASCADE,
    FOREIGN KEY (Topic_ID) REFERENCES Topic(Topic_ID) ON DELETE CASCADE
);

CREATE TABLE Location (
    Location_ID INT AUTO_INCREMENT PRIMARY KEY,
    Location_Type VARCHAR(20),
    Location_MeetingLink VARCHAR(255),
    Location_AddressLine1 VARCHAR(255),
    Location_City VARCHAR(80),
    Location_State VARCHAR(30),
    Location_Zip VARCHAR(10)
);

CREATE TABLE Session (
    Session_ID INT AUTO_INCREMENT PRIMARY KEY,
    Group_ID INT NOT NULL,
    Host_User_ID INT,
    Location_ID INT,
    Session_StartDateTime DATETIME,
    Session_EndDateTime DATETIME,
    Session_Capacity INT,
    Session_Notes TEXT,

    FOREIGN KEY (Group_ID) REFERENCES STUDY_GROUP(Group_ID) ON DELETE CASCADE,
    FOREIGN KEY (Host_User_ID) REFERENCES APP_USER(User_ID) ON DELETE SET NULL,
    FOREIGN KEY (Location_ID) REFERENCES Location(Location_ID) ON DELETE SET NULL
);

CREATE TABLE SessionRSVP (
    Session_ID INT NOT NULL,
    User_ID INT NOT NULL,
    SessionRSVP_Status BOOLEAN DEFAULT TRUE,
    SessionRSVP_Time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (Session_ID, User_ID),
    FOREIGN KEY (Session_ID) REFERENCES Session(Session_ID) ON DELETE CASCADE,
    FOREIGN KEY (User_ID) REFERENCES APP_USER(User_ID) ON DELETE CASCADE
);

-- Sample Data
INSERT INTO APP_USER (User_ID, User_Email, User_PasswordHash, User_DisplayName, User_Bio, User_AccountStatus)
VALUES
(1, 'alex@example.com', 'hash1', 'alex23', 'Computer science student looking for study partners.', 'Active'),
(2, 'brianna@example.com', 'hash2', 'briannaK', 'Enjoys group study for math and programming.', 'Active'),
(3, 'carlos@example.com', 'hash3', 'carlos_dev', 'Prefers evening study sessions.', 'Active'),
(4, 'dana@example.com', 'hash4', 'dana_sci', 'Interested in tutoring database concepts.', 'Active'),
(5, 'ethan@example.com', 'hash5', 'ethanM', 'Needs help with calculus and physics.', 'Active');

INSERT INTO Tutor (User_ID, Tutor_Expertise, Tutor_Availability)
VALUES
(2, 'Calculus, Algebra', 'Mon/Wed 5PM-8PM'),
(4, 'Databases, SQL, Python', 'Tue/Thu 4PM-7PM');

INSERT INTO Topic (Topic_ID, Topic_Name, Topic_Category)
VALUES
(1, 'SQL', 'Computer Science'),
(2, 'Database Design', 'Computer Science'),
(3, 'Calculus I', 'Mathematics'),
(4, 'Physics I', 'Science'),
(5, 'Python Programming', 'Computer Science');

INSERT INTO STUDY_GROUP (Group_ID, Group_Title, Group_Description, Group_PrivacyLevel, Group_SkillLevel, Owner_User_ID)
VALUES
(1, 'Database Systems Study Group', 'Study group for database design, SQL, and course review.', 'Public', 'Intermediate', 1),
(2, 'Calculus Review Group', 'Weekly review for derivatives, limits, and practice problems.', 'Public', 'Beginner', 2),
(3, 'Python Project Team', 'Collaborative coding and debugging practice.', 'Private', 'Intermediate', 4);

INSERT INTO GroupMembership (Group_ID, User_ID, GroupMembership_Role, GroupMembership_JoinStatus)
VALUES
(1, 1, 'Owner', TRUE),
(1, 3, 'Member', TRUE),
(1, 4, 'Tutor', TRUE),
(2, 2, 'Owner', TRUE),
(2, 5, 'Member', TRUE),
(3, 4, 'Owner', TRUE),
(3, 1, 'Member', TRUE),
(3, 3, 'Member', FALSE);

INSERT INTO GroupTopic (Group_ID, Topic_ID)
VALUES
(1, 1),
(1, 2),
(2, 3),
(3, 5);

INSERT INTO Location (Location_ID, Location_Type, Location_MeetingLink, Location_AddressLine1, Location_City, Location_State, Location_Zip)
VALUES
(1, 'Online', 'https://zoom.us/j/123456789', NULL, NULL, NULL, NULL),
(2, 'In-Person', NULL, '318 Meadow Brook Rd', 'Rochester', 'MI', '48309'),
(3, 'Online', 'https://meet.google.com/abc-defg-hij', NULL, NULL, NULL, NULL);

INSERT INTO Session (Session_ID, Group_ID, Host_User_ID, Location_ID, Session_StartDateTime, Session_EndDateTime, Session_Capacity, Session_Notes)
VALUES
(1, 1, 4, 1, '2026-04-15 18:00:00', '2026-04-15 19:30:00', 15, 'Review SQL joins and normalization.'),
(2, 2, 2, 2, '2026-04-16 17:00:00', '2026-04-16 18:30:00', 20, 'Calculus exam prep session.'),
(3, 3, 4, 3, '2026-04-17 19:00:00', '2026-04-17 20:30:00', 10, 'Work on Python project tasks.');

INSERT INTO SessionRSVP (Session_ID, User_ID, SessionRSVP_Status)
VALUES
(1, 1, TRUE),
(1, 3, TRUE),
(1, 4, TRUE),
(2, 2, TRUE),
(2, 5, TRUE),
(3, 1, TRUE),
(3, 3, FALSE),
(3, 4, TRUE);

CREATE OR REPLACE VIEW v_JustUsername AS
SELECT User_ID, User_DisplayName
FROM APP_USER;

-- Demo Queries

-- User account information
-- SELECT * FROM APP_USER WHERE User_ID = ?;

-- Groups a user belongs to
-- SELECT GroupMembership.User_ID, GroupMembership.GroupMembership_Role, STUDY_GROUP.Group_Title
-- FROM GroupMembership
-- JOIN STUDY_GROUP ON GroupMembership.Group_ID = STUDY_GROUP.Group_ID
-- WHERE GroupMembership.User_ID = ?;

-- Members in a group
-- SELECT STUDY_GROUP.Group_Title, APP_USER.User_DisplayName, GroupMembership.GroupMembership_Role, GroupMembership.GroupMembership_JoinStatus
-- FROM GroupMembership
-- JOIN APP_USER ON GroupMembership.User_ID = APP_USER.User_ID
-- JOIN STUDY_GROUP ON GroupMembership.Group_ID = STUDY_GROUP.Group_ID
-- WHERE STUDY_GROUP.Group_ID = ?;

-- Sessions for a group
-- SELECT STUDY_GROUP.Group_Title, Session.Session_ID, Session.Session_StartDateTime, Session.Session_EndDateTime, Session.Session_Notes
-- FROM Session
-- JOIN STUDY_GROUP ON Session.Group_ID = STUDY_GROUP.Group_ID
-- WHERE STUDY_GROUP.Group_ID = ?;

-- Groups by topic
-- SELECT Topic.Topic_Name, STUDY_GROUP.Group_Title
-- FROM GroupTopic
-- JOIN Topic ON GroupTopic.Topic_ID = Topic.Topic_ID
-- JOIN STUDY_GROUP ON GroupTopic.Group_ID = STUDY_GROUP.Group_ID
-- ORDER BY Topic.Topic_Name, STUDY_GROUP.Group_Title;

-- Tutors and expertise
-- SELECT APP_USER.User_DisplayName, Tutor.Tutor_Expertise, Tutor.Tutor_Availability
-- FROM Tutor
-- JOIN APP_USER ON Tutor.User_ID = APP_USER.User_ID;

-- RSVP responses for a session
-- SELECT SessionRSVP.Session_ID, APP_USER.User_DisplayName, SessionRSVP.SessionRSVP_Status
-- FROM SessionRSVP
-- JOIN APP_USER ON SessionRSVP.User_ID = APP_USER.User_ID
-- WHERE SessionRSVP.Session_ID = ?;
