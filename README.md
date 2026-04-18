# Student Study Group Finder

## Project Overview

Student Study Group Finder is a group project designed to help students find and join study groups based on shared classes, topics, and learning needs. The goal of the project is to make it easier for students to connect with others, organize study sessions, and collaborate more effectively.

## Features

- User registration and login with password hashing
- Create, join, leave, and delete study groups
- Group detail page showing members, sessions, RSVPs, and topics
- Session scheduling with online or in-person location support
- RSVP tracking for sessions
- Dashboard showing your groups and available groups
- Sample data for testing
- Full CRUD database operations (Create, Read, Update, Delete)

## Tools Used

- HTML
- CSS
- Python
- FastAPI
- MySQL
- MySQL Workbench

## Database Features

The database includes tables for:

- APP_USER
- Tutor
- STUDY_GROUP
- GroupMembership
- Topic
- GroupTopic
- Location
- Session
- SessionRSVP

The SQL file also includes:

- Sample insert data
- Reference queries for common operations
- Foreign key relationships
- Many-to-many relationship tables with composite primary keys

## Requirements

Install dependencies with:

```bash
pip install -r StudentStudyGroupFinder/requirements.txt
```

## Setup

1. Make sure MySQL is running
2. Open `Starter Code for 3450 Project.sql` in MySQL Workbench and run it to create and populate the database
3. Create a `.env` file inside the `StudentStudyGroupFinder/` folder with your database credentials:
   ```
   DB_HOST=localhost
   DB_USER=root
   DB_PASS=your_password
   DB_NAME=GroupFinderDB
   SECRET_KEY=any-random-string
   ```

## How to Run

```bash
cd StudentStudyGroupFinder
python3.13 -m uvicorn main:app --reload --port 8001
```

Then open your browser to `http://127.0.0.1:8001`
