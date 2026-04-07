-- creation
CREATE DATABASE GroupFinderDB;
USE GroupFinderDB;

-- User creation and permissions

CREATE USER 'MemberA'@'their IP Address' IDENTIFIED BY 'their password';
CREATE USER 'MemberB'@'their IP Address' IDENTIFIED BY 'their password';
CREATE USER 'MemberC'@'their IP Address' IDENTIFIED BY 'their password';
CREATE USER 'MemberD'@'their IP Address' IDENTIFIED BY 'their password';

GRANT SELECT, UPDATE, READ, DELETE UPDATE ON GroupFinderDB TO 'MemberA'@'their IP Address';
GRANT SELECT, UPDATE, READ, DELETE UPDATE ON GroupFinderDB TO 'MemberB'@'their IP Address';
GRANT SELECT, UPDATE, READ, DELETE UPDATE ON GroupFinderDB TO 'MemberC'@'their IP Address';
GRANT SELECT, UPDATE, READ, DELETE UPDATE ON GroupFinderDB TO 'MemberD'@'their IP Address';

-- Table creation

CREATE TABLE IF NOT EXISTS User(
    User_ID INT PRIMARY KEY,
    User_Email VARCHAR(255) NOT NULL,
    User_PasswordHash VARCHAR(255) NOT NULL UNIQUE,
    User_DisplayName VARCHAR(100) UNIQUE,
    User_Bio TEXT,
    User_CreatedAt TIMESTAMP,
    User_AccountStatus VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS Tutor(
    User_ID INT PRIMARY KEY,
    Tutor_Expertise VARCHAR(255),
    Tutor_Availability VARCHAR(255),

    FOREIGN KEY (User_ID) REFERENCES User(User_ID)
);

CREATE TABLE IF NOT EXISTS Group(
    Group_ID INT PRIMARY KEY,
    Group_Title VARCHAR(100),
    Group_Description TEXT,
    Group_PrivacyLevel VARCHAR(20),
    Group_SkillLevel VARCHAR(20),
    Group_CreatedAt TIMESTAMP,
    Owner_User_ID INT NOT NULL,

    FOREIGN KEY (Owner_User_ID) REFERENCES User(User_ID)
);

CREATE TABLE IF NOT EXISTS GroupMembership(
    Group_ID INT PRIMARY KEY,
    User_ID INT,
    GroupMembership_Role VARCHAR(35),
    GroupMembership_JoinStatus VARCHAR(20),
    GroupMembership_JoinedAt TIMESTAMP,

    FOREIGN KEY (Group_ID) REFERENCES Group(Group_ID),
    FOREIGN KEY (User_ID) REFERENCES User(User_ID)
);

CREATE TABLE IF NOT EXISTS Topic(
    Topic_ID INT PRIMARY KEY,
    Topic_Name VARCHAR(100),
    Topic_Category VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS GroupTopic(
    Group_ID INT PRIMARY KEY,
    Topic_ID INT NOT NULL,

    FOREIGN KEY (Group_ID) REFERENCES Group(Group_ID),
    FOREIGN KEY (Topic_ID) REFERENCES Topic(Topic_ID)
);

CREATE TABLE IF NOT EXISTS Location(
    Location_ID INT PRIMARY KEY,
    Location_Type VARCHAR(20),
    Location_MeetingLink VARCHAR(255),
    Location_AddressLine1 VARCHAR(255),
    Location_City VARCHAR(80),
    Location_State VARCHAR(30),
    Location_Zip VARCHAR(5)
);

CREATE TABLE IF NOT EXISTS Session(
    Session_ID INT PRIMARY KEY,
    Group_ID INT NOT NULL,
    Host_User_ID INT,
    Location_ID INT,
    Session_StartDateTime TIMESTAMP,
    Session_EndDateTime TIMESTAMP,
    Session_Capacity INT,
    Session_Notes TEXT,

    FOREIGN KEY (Group_ID) REFERENCES Group(Group_ID),
    FOREIGN KEY (Host_User_ID) REFERENCES User(User_ID),
    FOREIGN KEY (Location_ID) REFERENCES Location(Location_ID)
);

CREATE TABLE IF NOT EXISTS SessionRSVP(
    Session_ID INT PRIMARY KEY,
    User_ID INT,
    SessionRSVP_Status VARCHAR(20),
    SessionRSVP_Time TIMESTAMP,

    FOREIGN KEY (User_ID) REFERENCES User(User_ID),
    FOREIGN KEY (Session_ID) REFERENCES Session(Session_ID)
);


-- **************** Queries/functions ****************

-- user account information query; use to display user info on their account page



-- groups query, use to list all groups and their info that a user is a member of

-- (note for later: make this a cursor)
SELECT GroupMembership.User_ID, GroupMembership.GroupMembership_Role, Group.Group_Title,
FROM GroupMembership JOIN Group ON GroupMembership.Group_ID = Group.Group_ID
WHERE 